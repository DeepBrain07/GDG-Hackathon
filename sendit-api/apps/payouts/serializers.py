from rest_framework import serializers
from apps.payouts.models import Payout

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = "__all__"
        read_only_fields = ["id", "status", "reference", "created_at"]


# class WalletTransferSerializer(serializers.Serializer):
#     recipient_username = serializers.CharField()
#     amount = serializers.DecimalField(max_digits=12, decimal_places=2)

#     def validate(self, attrs):
#         sender = self.context['request'].user

#         if sender.username == attrs['recipient_username']:
#             raise serializers.ValidationError("Cannot transfer to yourself.")

#         try:
#             recipient_user = User.objects.get(username=attrs['recipient_username'])
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Recipient not found.")

#         attrs['recipient_user'] = recipient_user

#         # Check sender wallet balance
#         if sender.wallet.balance < attrs['amount']:
#             raise serializers.ValidationError("Insufficient wallet balance.")

#         return attrs

#     def create(self, validated_data):
#         sender = self.context['request'].user
#         recipient = validated_data['recipient_user']
#         amount = validated_data['amount']

#         # Create transaction
#         tx_ref = f"tx_{sender.id}_{recipient.id}_{int(amount*100)}_{int(time.time())}"
#         transaction = Transaction.objects.create(
#             wallet=sender.wallet,
#             tx_ref=tx_ref,
#             amount=amount,
#             status=Transaction.Status.SUCCESS  # internal transfer is instant
#         )

#         # Debit sender
#         sender.wallet.debit(amount, note=f"Transfer to {recipient.username}")

#         # Credit recipient
#         recipient.wallet.credit(amount, note=f"Transfer from {sender.username}")

#         # Ledger entries
#         WalletLedgerEntry.objects.create(
#             wallet=sender.wallet,
#             entry_type="debit",
#             amount=amount,
#             note=f"Transfer to {recipient.username}",
#             status="completed"
#         )

#         WalletLedgerEntry.objects.create(
#             wallet=recipient.wallet,
#             entry_type="credit",
#             amount=amount,
#             note=f"Transfer from {sender.username}",
#             status="completed"
#         )

#         return transaction
