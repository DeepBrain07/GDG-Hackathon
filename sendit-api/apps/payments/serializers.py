# wallets/serializers.py
from rest_framework import serializers
# from .models import Wallet, Transaction, WalletLedgerEntry
from django.contrib.auth import get_user_model
from .models import Transaction

User = get_user_model()

class WebFundingPayloadSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
