from django.db import models
from django.utils import timezone
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Escrow(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        FUNDED = "funded", "Funded"
        LOCKED = "locked", "Locked"
        RELEASE_READY = "release_ready", "Release Ready"
        RELEASED = "released", "Released"
        CANCELLED = "cancelled", "Cancelled"
        DISPUTED = "disputed", "Disputed"

    offer = models.OneToOneField(
        "offers.Offer",
        on_delete=models.CASCADE,
        related_name="escrow"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices)

    # in case of dispute
    released_amount_to_carrier = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # admin in that release fund
    released_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="released_escrows",
    )

    is_released = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["offer"])
        ]

    def __str__(self):
        return f"Escrow {self.id} for Offer {self.offer.id}"

    
