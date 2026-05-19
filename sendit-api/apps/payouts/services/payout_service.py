from django.conf import settings
from apps.payouts.models import Payout
from apps.payments.services.payment_service import PaymentService
import requests

class PayoutService:

    @staticmethod
    def release_funds(offer):
        """
        Release funds from escrow to carrier's bank account.
        Typically triggered by an admin.
        """
        escrow = offer.escrow

        if escrow.status != "release_ready":
            raise Exception("Escrow is not ready for release")

        # Create Payout record
        payout = Payout.objects.create(
            escrow=escrow,
            amount=escrow.amount,
            status=Payout.Status.INITIATED,
            reference=f"PAYOUT_{escrow.id}_{offer.code}",
            # These should ideally come from the carrier's profile/bank details
            bank_name=getattr(offer.carrier.profile, 'bank_name', 'Default Bank'),
            account_number=getattr(offer.carrier.profile, 'account_number', '0000000000')
        )

        # Call Interswitch payout API
        url = f"{settings.INTERSWITCH_BASE_URL}/transfers"
        
        access_token = PaymentService.get_interswitch_access_token()
        if not access_token:
            payout.mark_failed({"error": "Failed to authenticate with payment gateway"})
            raise Exception("Failed to authenticate with payment gateway")

        payload = {
            "amount": int(payout.amount * 100),
            "currency": "NGN",
            "destinationAccountNumber": payout.account_number,
            "destinationBankCode": "058",  # Should be dynamic based on bank_name
            "reference": payout.reference,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            payout.mark_success(response.json())
            escrow.release()
            return payout
        else:
            payout.mark_failed(response.json())
            raise Exception(f"Payout failed: {response.text}")

        return payout
