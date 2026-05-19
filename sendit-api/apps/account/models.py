from uuid import uuid4
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django_lifecycle import LifecycleModelMixin, hook, AFTER_UPDATE, AFTER_CREATE
from django_lifecycle.conditions import WhenFieldValueIs, WhenFieldValueWas
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework import status
from .manager import CustomBaseUserManager
from apps.core.models import Media

class VerifyOTP(models.Model):
    PURPOSE_CHOICES = [
        ('email', 'Email Verification'),
        ('password', 'Password Reset'),
        ('phone', 'Phone Verification'),
    ]
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    otp = models.CharField(max_length=64)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'purpose']),
            models.Index(fields=['phone_number', 'purpose']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.purpose} OTP for {self.email or self.phone_number}"


class CustomUser(LifecycleModelMixin, AbstractUser):
    """Custom User Model using Email as the primary identifier."""
    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    username = None
    email = models.EmailField(unique=True)
    agree_to_privacy_policy = models.BooleanField(default=False)

    objects = CustomBaseUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return self.get_full_name()

    @hook(AFTER_CREATE)
    def auto_create_profile(self):
        """Ensure a profile exists immediately upon user creation."""
        Profile.objects.get_or_create(
            user=self, 
            defaults={
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name
            }
        )

    @hook(AFTER_UPDATE, 
          condition=WhenFieldValueWas('is_active', False) & WhenFieldValueIs('is_active', True))
    def on_activation(self):
        """Keep your existing activation logic if you have specific activation-only tasks."""
        self.auto_create_profile()

    @property
    def get_jwt_tokens(self):
        try:
            refresh = RefreshToken.for_user(user=self)
            
            # Safely fetch is_new_user even if profile creation lagged
            profile = getattr(self, 'profile', None)
            is_new = profile.is_new_user if profile else True
            
            return {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'is_new_user': is_new
            }
        except TokenError as e:
            return {"error": str(e)}


class Profile(LifecycleModelMixin, models.Model):
    USER_TYPE_CHOICES = (
        ('sender', 'Sender'),
        ('carrier', 'Carrier'),
    )

    GENDER_CHOICES = (
        ('M', 'MALE'), ('F', 'FEMALE'), ('other', 'OTHER')
    )

    media = GenericRelation(Media)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        primary_key=True, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="carrier")
    email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)

    # Status tracking
    is_new_user = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=True, 
        help_text="True when user identification documents are approved."
    )
    
    location = models.ForeignKey(
        "core.Location", on_delete=models.SET_NULL, null=True, related_name="user_location"
    )

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def avatar(self):
        return self.media.filter(tag='avatar').first()

    @hook(AFTER_UPDATE, when_any=['first_name', 'last_name', 'email'], has_changed=True)
    def update_user_details(self):
        """Syncs changes back to the CustomUser model."""
        CustomUser.objects.filter(id=self.user.id).update(
            email=self.email, 
            first_name=self.first_name, 
            last_name=self.last_name
        )

    def __str__(self):
        return f'{self.user.email} profile'
    
    def get_age(self) -> int:
        """Calculates age from date_of_birth."""
        if self.date_of_birth:
            today = now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def delete(self, *args, **kwargs):
        """Ensures the User is deleted alongside the Profile."""
        try:
            user = CustomUser.objects.get(id=self.user_id)
            return user.delete()
        except CustomUser.DoesNotExist:
            return super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class Verification(models.Model):
    VERIFICATION_TYPES = (
        ('nin', 'NIN'),
        ('passport', 'Passport'),
        ('driver_license', 'Driver License'),
        ('voter_card', 'Voter Card'),
    )
    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    media = GenericRelation(Media)
    profile = models.ForeignKey(
        'Profile', on_delete=models.CASCADE, related_name='verifications'
    )
    verification_type = models.CharField(max_length=50, choices=VERIFICATION_TYPES)
    id_number = models.CharField(max_length=500, blank=True, null=True) # Stored encrypted
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='verified_verifications'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def documents(self):
        return self.media.filter(tag='document')

    @property
    def selfie_image(self):
        return self.media.filter(tag='selfie').first()

    def clean(self):
        """Validation logic for different ID types."""
        # We need to decrypt for validation if it's already encrypted (e.g. during a re-save)
        id_val = self.id_number
        if id_val and id_val.startswith('gAAAA'):
            try:
                f = Fernet(settings.ENCRYPTION_KEY)
                id_val = f.decrypt(id_val.encode()).decode()
            except Exception:
                pass # Keep as is if decryption fails
        
        # If you still want to ensure the field isn't empty:
        if not id_val:
            raise ValidationError("ID number is required")

        if self.verification_type == 'passport' and not id_val.isalnum():
            raise ValidationError("Passport number must be alphanumeric")
            
        # Optional: Keep a loose check just to prevent keyboard smashes
        if self.verification_type == 'voter_card' and len(id_val) < 5:
            raise ValidationError("Please enter a valid Voter card number")

    def save(self, *args, **kwargs):
        self.full_clean() # This triggers the clean() method above
        
        # Encrypt the ID number if it's not already encrypted
        if self.id_number and not self.id_number.startswith('gAAAA'):
            f = Fernet(settings.ENCRYPTION_KEY)
            self.id_number = f.encrypt(self.id_number.encode()).decode()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile.user.email} - {self.verification_type}"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['profile'],
                condition=models.Q(is_verified=True),
                name='unique_pending_verification_per_profile'
            )
        ]