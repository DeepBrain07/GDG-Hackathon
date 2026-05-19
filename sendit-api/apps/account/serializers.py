from rest_framework import serializers
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema_field # For fixing documentation warnings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.services.media_service import MediaService
from apps.core.serializers import MediaSerializer, LocationSerializer
from apps.core.models import Location
from .models import Profile, Verification

User = get_user_model()

# --- Auth Serializers ---

class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

class PasswordResetSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        try:
            validate_password(password=attrs['new_password'])
        except Exception as e:
            raise serializers.ValidationError(f"Password error: {e}")
        return attrs

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(max_length=30, write_only=True)
    confirm_password = serializers.CharField(max_length=30, write_only=True)
    # Nesting the profile allows the frontend to see is_new_user on login
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'agree_to_privacy_policy', 'password', 'confirm_password', 'profile')

    @extend_schema_field(serializers.JSONField())
    def get_profile(self, obj):
        try:
            return ProfileStatusSerializer(obj.profile).data
        except:
            return None

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        try:
            validate_password(attrs.get('password'))
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        attrs.pop('confirm_password', None)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(is_active=False, **validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=30, write_only=True)

    def validate(self, attrs):
        email, password = attrs.get('email'), attrs.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            return attrs
        raise serializers.ValidationError('Invalid Email or password!')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Include profile status in the JWT response for the frontend
        user_profile = self.user.profile 
        data['is_new_user'] = user_profile.is_new_user
        data['user_id'] = str(self.user.id)
        return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class PhoneOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=6)

class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()

# --- Profile Serializers ---

class ProfileStatusSerializer(serializers.ModelSerializer):
    """Minimal serializer for login/auth responses."""
    class Meta:
        model = Profile
        fields = ['is_new_user', 'type', 'is_verified']

class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, write_only=True)
    id = serializers.UUIDField(source='user_id', read_only=True)
    age = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    location = serializers.JSONField(write_only=True, required=False)
    location_details = LocationSerializer(source="location", read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'email', 'first_name', 'type', "image", 'avatar', 'last_name', 
            'date_of_birth', 'age', 'is_new_user', 'gender', 'bio', 
            'phone_number', 'phone_verified', "location_details", "location", 
            'created_at', 'updated_at', 'is_verified'
        )
        # Note: is_new_user is now read_only here; VerifyLayout will update it.
        read_only_fields = ["phone_verified", "is_verified", "email",]

    @extend_schema_field(serializers.IntegerField())
    def get_age(self, instance) -> int:
        return instance.get_age()

    @extend_schema_field(MediaSerializer)
    def get_avatar(self, obj):
        avatar = obj.avatar
        return MediaSerializer(avatar).data if avatar else None

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        location_data = validated_data.pop("location", None)

        if image is not None:
            MediaService.attach_file(image, instance, tag="avatar")

        if location_data is not None:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        return super().update(instance, validated_data)

# --- Verification Serializers ---

class VerificationSerializer(serializers.ModelSerializer):
    document = serializers.FileField(write_only=True, required=False)
    selfie = serializers.ImageField(write_only=True, required=False)
    documents = serializers.SerializerMethodField(read_only=True)
    selfie_image = serializers.SerializerMethodField(read_only=True)
    verification_id = serializers.SerializerMethodField(read_only=True)
    profile = UserSerializer(read_only=True)

    class Meta:
        model = Verification
        fields = [
            'verification_id', 'profile', 'verification_type', 'id_number',
            'document', "documents", 'selfie', "selfie_image",
            'is_verified', 'note', 'verified_by', 'verified_at'
        ]
        read_only_fields = ['is_verified', 'note', 'verified_by', 'verified_at', 'profile']

    def to_representation(self, instance):
        """Decrypt the ID number for owner or admin."""
        ret = super().to_representation(instance)
        user = self.context.get('request').user if self.context.get('request') else None
        
        if user and instance.id_number:
            # Check if user is staff or the owner of this verification
            if user.is_staff or (hasattr(user, 'profile') and user.profile == instance.profile):
                try:
                    f = Fernet(settings.ENCRYPTION_KEY)
                    ret['id_number'] = f.decrypt(instance.id_number.encode()).decode()
                except Exception:
                    # If decryption fails (e.g. data already plain or wrong key), 
                    # keep original or return as is
                    pass
            else:
                # Mask for anyone else (though queryset should already restrict)
                ret['id_number'] = "********"
        return ret

    @extend_schema_field(MediaSerializer(many=True))
    def get_documents(self, obj):
        return MediaSerializer(obj.documents, many=True).data

    @extend_schema_field(serializers.UUIDField())
    def get_verification_id(self, obj):
        return obj.id 

    @extend_schema_field(MediaSerializer)
    def get_selfie_image(self, obj):
        media = obj.selfie_image
        return MediaSerializer(media).data if media else None

    def create(self, validated_data):
        # 1. Pop files and profile out of validated_data
        document = validated_data.pop('document', None)
        selfie = validated_data.pop('selfie', None)
        
        # Check if profile was passed by the view (perform_create)
        # If not, get it from the request context
        profile = validated_data.pop('profile', None)
        if not profile:
            profile = self.context['request'].user.profile

        # 2. Check for pending verifications
        if Verification.objects.filter(profile=profile, is_verified=False).exists():
            raise serializers.ValidationError("You already have a pending verification")

        # 3. Create the instance safely
        # We pass profile explicitly here, and it's no longer in validated_data
        verification = Verification.objects.create(profile=profile, **validated_data)

        # 4. Handle Media Attachments
        if document:
            MediaService.attach_file(document, verification, tag='document')
        else:
            # If you want it required, the Serializer field should handle this, 
            # but this is a safe fallback
            raise serializers.ValidationError({"document": "This field is required."})

        if selfie:
            MediaService.attach_file(selfie, verification, tag='selfie')
        else:
            raise serializers.ValidationError({"selfie": "This field is required."})

        return verification
    
    def update(self, instance, validated_data):
        document_file = validated_data.pop('document', None)
        selfie_file = validated_data.pop('selfie', None)

        instance = super().update(instance, validated_data)

        if document_file:
            MediaService.attach_file(document_file, instance, tag='document')
        if selfie_file:
            MediaService.attach_file(selfie_file, instance, tag='selfie')

        return instance

class ReviewVerificationSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(required=True)
    class Meta:
        model = Verification
        fields = ['is_verified', 'note']

    def validate(self, attrs):
        if attrs.get('is_verified') is False and not attrs.get('note', '').strip():
            raise serializers.ValidationError({'note': 'You must provide a note when un-verifying.'})
        return attrs
