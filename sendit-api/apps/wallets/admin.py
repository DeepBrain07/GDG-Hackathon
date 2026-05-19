from django.contrib import admin
from .models import Wallet, WalletLedgerEntry


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "balance",
        "virtual_account_number",
        "virtual_account_bank_number",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "virtual_account_number",
        "virtual_account_bank_number",
    )
    list_filter = ("updated_at", "created_at")
    # readonly_fields = ("balance", "created_at", "updated_at")

    fieldsets = (
        ("User Info", {
            "fields": ("user", "balance")
        }),
        ("Virtual Account Details", {
            "fields": (
                "virtual_account_name",
                "virtual_account_number",
                "virtual_account_bank_number",
            )
        }),
    )


@admin.register(WalletLedgerEntry)
class WalletLedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "entry_type",
        "amount",
        "note",
        "created_at",
    )
    search_fields = (
        "wallet__user__username",
        "note",
    )
    list_filter = ("entry_type", "created_at")
    readonly_fields = ("wallet", "entry_type", "amount", "note", "created_at")

    ordering = ("-created_at",)
