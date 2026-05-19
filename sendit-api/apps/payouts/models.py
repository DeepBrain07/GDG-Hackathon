from django.db import models

# Create your models here.


class Payout(models.Model):

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    escrow = models.OneToOneField(
        "escrow.Escrow",
        on_delete=models.CASCADE,
        related_name="payout"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)

    status = models.CharField(max_length=20, choices=Status.choices)

    reference = models.CharField(max_length=100, unique=True)

    response_payload = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def mark_success(self, payload=None):
        self.status = self.Status.SUCCESS
        self.response_payload = payload
        self.save()

    def mark_failed(self, payload=None):
        self.status = self.Status.FAILED
        self.response_payload = payload
        self.save()
