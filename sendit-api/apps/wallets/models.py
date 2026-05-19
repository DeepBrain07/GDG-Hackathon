from django.db import models
from django.conf import settings

User =  settings.AUTH_USER_MODEL

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    virtual_account_name = models.CharField(max_length=20, null=True, blank=True)
    virtual_account_number = models.CharField(max_length=20, null=True, blank=True)
    virtual_account_bank_number = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.balance}"

    def credit(self, amount, note=""):
        WalletLedgerEntry.objects.create(wallet=self, entry_type="credit", amount=amount, note=note)
        self.balance += amount
        self.save(update_fields=["balance"])

    def debit(self, amount, note=""):
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        WalletLedgerEntry.objects.create(wallet=self, entry_type="debit", amount=amount, note=note)
        self.balance -= amount
        self.save(update_fields=["balance"])


class WalletLedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        CREDIT = "credit"
        DEBIT = "debit"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="ledger_entries")
    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["wallet", "entry_type"]),
        ]

    def __str__(self):
        return f"{self.entry_type.title()} {self.amount} for {self.wallet.user.username}"