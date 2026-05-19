import uuid
from django.db import models
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from apps.core.models import Media, Location
from decimal import Decimal
import string  
import random  
from django.db import models
from django.conf import settings

class Offer(models.Model):

    class PackageType(models.TextChoices):
        SMALL = "small", "Small"
        MEDIUM = "medium", "Medium"
        LARGE = "large", "Large"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"
        ACCEPTED = "accepted", "Accepted"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        DISPUTED = "disputed", "Disputed"

    class Step(models.TextChoices):
        DETAILS = "details"
        LOCATION = "location"
        PRICING = "pricing"
        REVIEW = "review"
        POSTED = "posted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=10, unique=True)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_offers")
    carrier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="carried_offers")

    # DETAILS
    package_type = models.CharField(
        max_length=10, choices=PackageType.choices, null=True, blank=True)
    is_fragile = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    media = GenericRelation(Media)

    # LOCATION
    pickup_location = models.ForeignKey(
        "core.Location", on_delete=models.SET_NULL, null=True, related_name="pickup_offers")
    delivery_location = models.ForeignKey(
        "core.Location", on_delete=models.SET_NULL, null=True, related_name="delivery_offers")
    pickup_time = models.DateTimeField(null=True, blank=True)
    # RECEIVER
    receiver_name = models.CharField(max_length=255, blank=True)
    receiver_phone = models.CharField(max_length=20, blank=True)

    # PRICING
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    urgent_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    platform_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    is_urgent = models.BooleanField(default=False)

    
    # FLOW CONTROL
    current_step = models.CharField(
        max_length=20, choices=Step.choices, default=Step.DETAILS)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "is_urgent"]),
            models.Index(fields=["status", "total_price"]),
            models.Index(fields=["pickup_location"]),
            models.Index(fields=["delivery_location"]),
        ]

    def __str__(self):
        return f"{self.code} | {self.sender} | {self.status}"

    @property
    def image(self):
        return self.media.filter(tag='thumbnail').first() or ""
    
    @property
    def carrier_price(self):
        return Decimal(self.total_price - self.platform_fee) if self.total_price else Decimal(0)

    # -------------------------
    # BUSINESS LOGIC
    # -------------------------
    def calculate_pricing(self):
        if self.base_price is None:
            return Decimal(0)

        self.platform_fee = self.base_price * Decimal(settings.OFFER_PLATFORM_FEE) # in percentage
        self.urgent_fee = Decimal(settings.OFFER_URGENT_FEE) if self.is_urgent else 0
        self.total_price = self.base_price + self.urgent_fee + self.platform_fee  

    def validate_step(self,step=None):
        """Validate only what is required at current step"""
        if not step:
            step = self.current_step
        
        if step == self.Step.DETAILS:
            if not self.package_type:
                raise ValidationError("Package type is required")
            
        elif step == self.Step.LOCATION:
            if not self.pickup_location or not self.delivery_location:
                raise ValidationError(
                    "Both pickup and delivery locations are required")

        elif step == self.Step.PRICING:
            if self.base_price is None:
                raise ValidationError("Base price is required")

        elif step == self.Step.REVIEW:
            if not self.is_complete():
                raise ValidationError("Offer is not complete")

    def is_complete(self):
        """Check if offer is complete validate and return error"""

        errors = {}
        if not self.package_type:
            errors["package_type"] = "Package type is required"
        if not self.pickup_location or not self.delivery_location:
            errors["location"] = "Both pickup and delivery locations are required"
        if self.base_price is None:
            errors["base_price"] = "Base price is required"
        if not self.receiver_name:
            errors["receiver_name"] = "Receiver name is required"
        if not self.receiver_phone:
            errors["receiver_phone"] = "Receiver phone is required"
        if not self.platform_fee:
            errors["platform_fee"] = "Platform fee is required"
        if not self.total_price:
            errors["total_price"] = "Total price is required"
        if self.is_urgent and not self.urgent_fee:
            errors["is_urgent"] = "Urgent fee is required"

        if errors:
            raise ValidationError(errors)
        return True

        # return all([
        #     self.package_type,
        #     self.pickup_location,
        #     self.delivery_location,
        #     self.base_price,
        #     self.receiver_name,
        #     self.receiver_phone,
        # ])

    def clean(self):
        """Django built-in validation hook"""
        self.validate_step()
    
    def generate_offer_code(self):
        """
        Generates a unique random alphanumeric code.
        Example: PK-A7B2C9
        """
        prefix = "PK-"
        length = 6
        characters = string.ascii_uppercase + string.digits
        
        while True:
            # Generate a random 6-character string
            random_part = ''.join(random.choices(characters, k=length))
            code = f"{prefix}{random_part}"
            
            # Check if this code already exists
            if not Offer.objects.filter(code=code).exists():
                self.code = code
                break

    def save(self, *args, **kwargs):
        # Only generate code if it doesn't exist
        if not self.code:
            self.generate_offer_code()
        
        # Ensure pricing is calculated before saving
        self.calculate_pricing()
        
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.code:
            self.generate_offer_code()
        self.calculate_pricing()
        super().save(*args, **kwargs)


class Proposal(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    uuid = models.UUIDField( default=uuid.uuid4, editable=False)
    offer = models.ForeignKey("offers.Offer", on_delete=models.CASCADE, related_name="proposals")
    carrier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.offer.code} - {self.carrier.username}"


class OfferImpression(models.Model):
    uuid = models.UUIDField( default=uuid.uuid4, editable=False)

    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='impressions')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True)

    session_key = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('offer', 'user'), ('offer', 'session_key')]
        indexes = [
            models.Index(fields=['offer', 'user']),
            models.Index(fields=['offer', 'session_key']),
        ]


#  # DETAILS
#     package_type
#     is_fragile 
#     description 
#     media 
    
#     # LOCATION
#     pickup_location  {
#     city
#     area 
#     street 
#     landmark
#     latitude 
#     longitude 

#     }
#     delivery_location {
#           city
#     area 
#     street 
#     landmark
#     latitude 
#     longitude 
#     }
#     pickup_time 
#     receiver_name
#     receiver_phone 


#     # PRICING
#     base_price
#     is_urgent

