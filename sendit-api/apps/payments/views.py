from rest_framework import permissions, status
import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.payments.services.webhook import PaymentVerifyWebhookService
from apps.wallets.services.wallet_services import WalletService
from .services.payment_service import PaymentService
from apps.payments.serializers import WebFundingPayloadSerializer
from .utils import verify_signature
from .documentation.payments.schemas import web_funding_create_payload_doc, web_funding_upload_payload_doc
from .serializers import TransactionSerializer
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class InterswitchWebhookView(APIView):
    """
    Webhook endpoint for Interswitch payment notifications.
    WEB PAYLOAD :
    {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "event": "TRANSACTION.COMPLETED",
        "data": {
            "responseCode": "00",
            "amount": 500000,  // amount in kobo/cents (5000.00 NGN)
            "channel": "WEB",
            "merchantReference": "TXN_987654321", `tx_ref we included`
            "transactionDate": "2026-03-25T10:30:00Z",
            "customerEmail": "user@example.com"
        }
        }


        Transfer:
        {
        "uuid": "987e6543-e21b-12d3-a456-426614174999",
        "event": "TRANSACTION.COMPLETED",
        "data": {
            "responseCode": "00",
            "amount": 1000000,  // 10,000.00 NGN
            "channel": "TRANSFER",
            "retrievalReferenceNumber": "1234567890",  `account number`
            "transactionDate": "2026-03-25T12:45:00Z",
            "payerName": "John Doe",
            "payerAccount": "0123456789"
        }
        }
    """
    authentication_classes = []  # Public endpoint
    permission_classes = []

    def post(self, request):
        # 🔴 verify signature

        secret = settings.INTERSWITCH_WEBHOOK_SECRET
        raw_body = request.body
        signature = request.headers.get("X-Interswitch-Signature")

        if not signature:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not verify_signature(raw_body, signature, secret):
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload =json.loads(raw_body)   
            if payload.get("event") != "TRANSACTION.COMPLETED":
                return Response(status=200)

            PaymentVerifyWebhookService.handle(payload)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error here
            logger.error(f"[InterswitchWebhookView] Error: {e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)


@web_funding_create_payload_doc
class WebFundingPayloadView(APIView):
    """
    Handles wallet top-up through web:
    - Generates transaction
    - Returns payload for frontend inline payment
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WebFundingPayloadSerializer

    def post(self, request):
        """
        Provide details user can use to make payment (inline form) 
        and transaction status INITIATED
        """
        amount = request.data.get("amount")
        user = request.user

        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        wallet = getattr(user, "wallet", None)
        if not wallet:
            wallet = WalletService.create_wallet_account(user)

        try:
            transaction, payload = PaymentService.create_funding_payload(
                user=request.user,
                amount=float(amount)
            )

            return Response({
                "message": "Funding initiated",
                "form_payload": payload,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@web_funding_upload_payload_doc
class WebFundingUploadPayloadView(APIView):
    """
    Handles wallet funding update through web:
    - Updates transaction
    - Returns success message
    """
    permission_classes = [permissions.IsAuthenticated]
    # serializer_class = WebFundingPayloadSerializer

    def post(self, request):
        """
        Provide details user can use to update payment (inline form) 
        and transaction status SUCCESS
        """
        data = request.data
        print(data)
        amount = data.get("amount") or data.get("Amount")
        user = request.user
        txn_ref = data.get("txnRef") or data.get("TxnRef") or data.get("MerchantReference")
        response_code = data.get("resp") or data.get("Resp") or data.get("ResponseCode")

        if response_code not in ["200","00","201"]:
            return Response({"error": "Transaction not successful"}, status=status.HTTP_400_BAD_REQUEST)

        if not txn_ref or not amount:
            return Response({"error": "Invalid payload txnRef and amount missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet = getattr(user, "wallet", None)
        if not wallet:
            wallet = WalletService.create_wallet_account(user)

        try:
            transaction = PaymentService.update_funding_payload(
                user=request.user,
                amount=float(amount),
                txn_ref=txn_ref,
                data=data
            )

            return Response({
                "message": "Funding successfully",
                "transaction_data": TransactionSerializer(transaction).data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
