from django.db import transaction
from apps.payments.models import Transaction
from apps.core.services.notification_service import NotificationService, Notification
from apps.wallets.models import Wallet, WalletLedgerEntry


class PaymentVerifyWebhookService:
    """
    Service to handle wallet funding webhooks from Interswitch.
    """
    @classmethod
    def handle(cls,payload):
        """
        Handle a successful payment from Interswitch.
        - Marks transaction as success
        - Marks escrow as funded
        - Notifies the sender
        """
        if payload.get("event") != "TRANSACTION.COMPLETED":
            return

        data = payload.get("data", {})

        # ✅ only success
        if data.get("responseCode") != "00":
            return

        uuid = payload.get("uuid")

        # ✅ idempotency
        if Transaction.objects.filter(external_id=uuid).exists():
            return

        amount = data.get("amount") / 100
        channel = data.get("channel")

        transaction_obj = None

        with transaction.atomic():
            # =========================
            # 🔵 WEB CHECKOUT
            # =========================
            if channel == "WEB":
                tx_ref = data.get("merchantReference")

                transaction_obj = Transaction.objects.filter(
                    tx_ref=tx_ref).select_related("wallet").first()
                if not transaction_obj:
                    raise Exception(f"Transaction not found: {tx_ref}")

            # =========================
            # 🟢 BANK TRANSFER (STATIC ACCOUNT)
            # =========================
            elif channel == "TRANSFER":
                account_number = data.get("retrievalReferenceNumber")

                wallet = Wallet.objects.filter(
                    account_number=account_number).first()
                if not wallet:
                    raise Exception(
                        f"Wallet not found for account {account_number}")

                # create transaction on the fly
                transaction_obj = Transaction.objects.create(
                    tx_ref=f"transfer_{uuid}",
                    wallet=wallet,
                    amount=amount,
                    status=Transaction.Status.INITIATED
                )
            else:
                return  # ignore other channels for now

            # =========================
            # ✅ FINALIZE TRANSACTION
            # =========================
            transaction_obj.external_id = uuid

            cls.finalize_payment_success(transaction=transaction_obj, payload=payload, channel=channel)

        # ✅ notify user outside atomic block to avoid issues if notification fails
        NotificationService.create(
            user=wallet.user,
            type=Notification.Type.PAYMENT_SUCCESS,
            title="Payment Successful",
            message=f"Your payment of {transaction_obj.amount} has been received via {channel}.",
            content_object=transaction_obj
        )

        return transaction_obj
    
    @classmethod
    def finalize_payment_success(cls,transaction:Transaction,payload, channel):
        print('>>>>>>>>> finalize payment init<<<<<')
        transaction.mark_success(payload)

        wallet = transaction.wallet

        # ✅ credit wallet
        amount = transaction.amount
        wallet.balance += amount
        wallet.save()

        # ✅ ledger
        WalletLedgerEntry.objects.create(
            wallet=wallet,
            entry_type=WalletLedgerEntry.EntryType.CREDIT,
            amount=amount,
            note=f"Wallet funded via {channel}"
        )
        print(f"[finalize payment success] finalize payment{payload}")


    
    
