from django.contrib import admin
from .models import Escrow
# Register your models here.
@admin.register(Escrow)
class EscrowAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "offer",
        "status",
        "amount",
        "created_at",
    )
    list_editable = (
        "status",
    )
