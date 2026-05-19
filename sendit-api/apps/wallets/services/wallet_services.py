from django.db.models import Sum, Case, When, DecimalField
from django.conf import settings
import requests
from apps.wallets.models import Wallet
from apps.payments.services.payment_service import PaymentService
from apps.escrow.models import Escrow

import logging

logger = logging.getLogger(__name__)

class WalletService:
    @staticmethod
    def create_wallet_account(user):
        """
        Creates a virtual account for the user via Interswitch.
        If in DEBUG mode and Interswitch fails, creates a mock wallet to prevent app crashes.
        """
        # 1. Check if wallet already exists with an account number
        wallet, created = Wallet.objects.get_or_create(user=user)
        if wallet.virtual_account_number:
            return wallet

        try:
            # 2. Attempt to get Interswitch Access Token
            access_token = PaymentService.get_interswitch_access_token()
            
            if not access_token:
                if settings.DEBUG:
                    logger.warning(f"⚠️ Interswitch Auth failed in DEBUG. Creating MOCK wallet for: {user.email}")
                    return WalletService._create_mock_wallet(wallet, user)
                else:
                    logger.error("❌ Interswitch Authentication failed in Production.")
                    raise Exception("Failed to authenticate with Interswitch")

            # 3. Prepare Interswitch API Request
            payload = {
                "accountName": f"{user.full_name}",
                "merchantCode": settings.INTERSWITCH_MERCHANT_CODE,
                "provider": "WEMA"
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{settings.INTERSWITCH_BASE_URL}/paymentgateway/api/v1/payable/virtualaccount",
                json=payload,
                headers=headers,
                timeout=15
            )
            
            logger.info(f"[Wallet API Response] Status: {response.status_code}")

            # 4. Handle Successful API Response
            if response.status_code in [200, 201]:
                data = response.json()
                wallet.virtual_account_name = data.get("accountName", user.full_name)
                wallet.virtual_account_number = data.get("accountNumber")
                wallet.virtual_account_bank_number = data.get("bankName", "WEMA BANK")
                wallet.provider = data.get("bankCode", "WEMA")
                wallet.balance = 0
                wallet.save()
                return wallet
            
            # 5. Handle API Failure (e.g., 400, 500)
            else:
                if settings.DEBUG:
                    logger.warning(f"⚠️ Interswitch API returned {response.status_code}. Falling back to MOCK.")
                    return WalletService._create_mock_wallet(wallet, user)
                
                logger.error(f"❌ Interswitch API Error: {response.text}")
                raise Exception(f"Interswitch API error: {response.status_code}")

        except requests.RequestException as e:
            logger.error(f"❌ Network error creating virtual account: {e}")
            if settings.DEBUG:
                return WalletService._create_mock_wallet(wallet, user)
            raise Exception(f"Failed to connect to payment provider: {e}")

    @staticmethod
    def _create_mock_wallet(wallet, user):
        """Helper to populate wallet with fake data for local testing."""
        wallet.virtual_account_name = f"DEV-{user.full_name}"
        wallet.virtual_account_number = f"99{user.id}008877"
        wallet.virtual_account_bank_number = "WEMA BANK (TEST)"
        wallet.provider = "WEMA"
        wallet.balance = 0
        wallet.save()
        return wallet

    @staticmethod
    def get_breakdown(user):
        data = Escrow.objects.filter(
            offer__carrier=user
        ).aggregate(
            locked=Sum(
                Case(
                    When(status="locked", then="amount"),
                    output_field=DecimalField()
                )
            ),
            available=Sum(
                Case(
                    When(status="release_ready", then="amount"),
                    output_field=DecimalField()
                )
            ),
            total_earned=Sum(
                Case(
                    When(status="released", then="amount"),
                    output_field=DecimalField()
                )
            ),
        )

        return {
            "wallet_balance": getattr(user.wallet, 'balance', 0),
            "locked": data["locked"] or 0,
            "release_ready": data["available"] or 0,
            "total_earned": data["total_earned"] or 0,
        }

    @staticmethod
    def get_full_history(wallet):
        ledger_qs = wallet.ledger_entries.all().values(
            "id", "amount", "entry_type", "note", "created_at"
        )

        tx_qs = wallet.transactions.all().values(
            "id", "amount", "status", "tx_ref", "created_at"
        )

        ledger_data = [
            {
                "id": item["id"],
                "type": "ledger",
                "sub_type": item["entry_type"],
                "amount": item["amount"],
                "note": item["note"],
                "status": "completed",
                "created_at": item["created_at"],
            }
            for item in ledger_qs
        ]

        tx_data = [
            {
                "id": item["id"],
                "type": "transaction",
                "sub_type": "funding",
                "amount": item["amount"],
                "note": item["tx_ref"],
                "status": item["status"],
                "created_at": item["created_at"],
            }
            for item in tx_qs
        ]

        combined = ledger_data + tx_data
        return sorted(combined, key=lambda x: x["created_at"], reverse=True)