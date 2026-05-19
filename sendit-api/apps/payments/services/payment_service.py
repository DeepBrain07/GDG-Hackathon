from django.conf import settings
from django.core.exceptions import PermissionDenied
import requests
import base64
from decimal import Decimal
from apps.payments.models import Transaction
from apps.core.services.notification_service import NotificationService,Notification
from .webhook import PaymentVerifyWebhookService
import uuid


class PaymentService:

    @staticmethod
    def get_interswitch_access_token():
        url = f"{settings.INTERSWITCH_BASE_URL}/passport/oauth/token?grant_type=client_credentials"

        # Interswitch usually uses basic auth for token generation
        auth_str = f"{settings.INTERSWITCH_CLIENT_ID}:{settings.INTERSWITCH_CLIENT_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "grant_type": "client_credentials",
            "scope": "profile"
        }
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                return response.json().get("access_token")
            return None
        except requests.RequestException as e:
            print(f"Error fetching access token: {e}")
            return None

    @staticmethod
    def create_funding_payload(user, amount):
        """
        Initiate wallet funding via payment gateway (Interswitch).
        - Creates a transaction in INITIATED status.
        - Returns payload frontend can use to render inline form.
        """

        # 1️⃣ Check user verification
        if not getattr(user.profile, "is_verified", False):
            raise PermissionDenied("Only verified users can fund wallet")

        # 2️⃣ Ensure wallet exists
        wallet = getattr(user, "wallet", None)
        if not wallet:
            # wallet = WalletService.create_wallet_account(user)
            raise ValueError("No wallet linked to user account")

        # 3️⃣ Generate unique transaction reference
        tx_ref = f"Wallet_{uuid.uuid4().hex[:16]}_{int(amount*100)}"

        # 4️⃣ Create transaction record
        transaction = Transaction.objects.create(
            wallet=wallet,
            tx_ref=tx_ref,
            amount=amount,
            status=Transaction.Status.INITIATED
        )

        # 5️⃣ Prepare payload for frontend inline form
        payload = {
            "tx_ref": tx_ref,                        # required by Interswitch
            "amount": int(round(amount * 100)),      # convert NGN to kobo
            "currency": "NGN",
            "site_redirect_url": settings.INTERSWITCH_CALLBACK_URL,
            "interswitch_payment_url": f"{settings.INTERSWITCH_BASE_URL}/collections/w/pay",
            "customer_email": user.email,
            "customer_mobile": getattr(user.profile, "phone_number", None),
        }

        return transaction, payload
  
    @staticmethod
    def update_funding_payload(user, amount, txn_ref, data):
        """
        update wallet funding via response from payment gateway (Interswitch).
        - Creates a transaction with SUCCESS status.
        - Returns success message.
        """
        channel = "WEB"

        # 1️⃣ Check user verification
        if not getattr(user.profile, "is_verified", False):
            raise PermissionDenied("Only verified users can fund wallet")

        # 2️⃣ Ensure wallet exists
        wallet = getattr(user, "wallet", None)
        if not wallet:
            # wallet = WalletService.create_wallet_account(user)
            raise ValueError("No wallet linked to user account")

        # 3️⃣ Generate unique transaction reference
        # tx_ref = f"Wallet_{uuid.uuid4().hex[:16]}_{int(amount*100)}"

        # 4️⃣ Create transaction record
        transaction = Transaction.objects.create(
            wallet=wallet,
            tx_ref=txn_ref,
            amount=Decimal(amount / 100),
            status=Transaction.Status.SUCCESS
        )

        PaymentVerifyWebhookService.finalize_payment_success(transaction=transaction, channel=channel,payload=data)
         # ✅ notify user outside atomic block to avoid issues if notification fails
        NotificationService.create(
            user=wallet.user,
            type=Notification.Type.PAYMENT_SUCCESS,
            title="Payment Successful",
            message=f"Your payment of {transaction.amount} has been received via {channel}.",
            content_object=transaction
        )


        return transaction

    @staticmethod
    def notify_payment_status(transaction):
        """
        Called after Interswitch confirms payment.
        - Marks transaction SUCCESS
        - Credits wallet
        - Sends notification to user
        """

        # 3️⃣ Notify user
        NotificationService.create(
            user=transaction.wallet.user,
            type="payment_success",
            title="Wallet Funded",
            message=f"Your wallet has been funded with NGN {transaction.amount:.2f}",
            content_object=transaction
        )
