from rest_framework import serializers
from .models import Wallet
from .services.wallet_services import WalletService
from django.urls import reverse

class WalletSerializer(serializers.ModelSerializer):
     class Meta:
        model = Wallet
        fields = [
            "id",
            "balance",
            
        ]

class WalletDashboardSerializer(serializers.ModelSerializer):
    breakdown = serializers.SerializerMethodField()
    virtual_account = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            "balance",
            "virtual_account",
            "breakdown",
            "actions",
        ]

    def get_breakdown(self, obj):
        if not hasattr(self, "_breakdown"):
            self._breakdown = WalletService.get_breakdown(obj.user)

        return {
            "locked": self._breakdown["locked"],
            "release_ready": self._breakdown["release_ready"],
            "total_earned": self._breakdown["total_earned"],
        }

    def get_virtual_account(self, obj):
        return {
            "account_name": obj.virtual_account_name,
            "account_number": obj.virtual_account_number,
            "bank": obj.virtual_account_bank_number,
        }

    def get_actions(self, obj):
        request = self.context.get("request")

        return {
            "fund_wallet": "/wallet/fund/",
            "view_history": "/wallet/history/",
            "withdraw": "/wallet/withdraw/",
        }



class WalletHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()        # ledger / transaction
    sub_type = serializers.CharField()    # credit / debit / funding
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    # optional UX improvements
    direction = serializers.SerializerMethodField()

    def get_direction(self, obj):
        """
        Helps frontend easily style:
        credit = green, debit = red
        """
        if obj["type"] == "ledger":
            return "in" if obj["sub_type"] == "credit" else "out"

        if obj["type"] == "transaction":
            return "in" if obj["status"] == "success" else "pending"

        return "neutral"