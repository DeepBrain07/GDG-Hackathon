from django.contrib import admin
from .models import Offer, Proposal

class ProposalInline(admin.TabularInline):
    model = Proposal
    extra = 0
    readonly_fields = ("carrier", "price", "status")

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):

    # -------------------------
    # LIST VIEW (table)
    # -------------------------
    inlines = [ProposalInline]
    list_display = (
        "code",
        "sender",
        "carrier",
        "status",
        "current_step",
        "is_urgent",
        "total_price",
        "created_at",
    )
    list_editable = (
        "status",
        "current_step",
        "is_urgent",
    )

    list_filter = (
        "status",
        "current_step",
        "is_urgent",
        "package_type",
        "created_at",
    )

    search_fields = (
        "code",
        "sender__email",
        "receiver_name",
        "receiver_phone",
    )

    ordering = ("-created_at",)

    # -------------------------
    # DETAIL VIEW ORGANIZATION
    # -------------------------
    fieldsets = (

        ("Basic Info", {
            "fields": ("code", "sender", "carrier", "status", "current_step")
        }),

        ("Package Details", {
            "fields": ("package_type", "is_fragile", "description")
        }),

        ("Locations", {
            "fields": ("pickup_location", "delivery_location", "pickup_time")
        }),

        ("Pricing", {
            "fields": (
                "base_price",
                "is_urgent",
                "urgent_fee",
                "platform_fee",
                "total_price",
            )
        }),

        ("Receiver Info", {
            "fields": ("receiver_name", "receiver_phone")
        }),

        ("Metadata", {
            "fields": ("created_at",)
        }),
    )

    readonly_fields = (
        "code",
        "platform_fee",
        "urgent_fee",
        "total_price",
        "created_at",
    )

    # -------------------------
    # PERFORMANCE
    # -------------------------
    list_select_related = (
        "sender",
        "carrier",
        "pickup_location",
        "delivery_location",
    )

    # -------------------------
    # SAFETY (optional but recommended)
    # -------------------------
    def has_delete_permission(self, request, obj=None):
        # prevent accidental deletion in production
        return True  # change to False if needed
    

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "offer",
        "carrier",
        "price",
        "status",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "offer__code",
        "carrier__email",
    )

    list_select_related = (
        "offer",
        "carrier",
    )