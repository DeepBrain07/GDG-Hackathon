from ..models import Escrow
from apps.wallets.models import WalletLedgerEntry
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone
from django.db import transaction as db_transaction
from apps.core.services.notification_service import NotificationService, Notification

class EscrowService:
    """
    Phases in the workflow
    Offer accepted → create escrow (PENDING)
    Check sender wallet → fund escrow (FUNDED)
    Sender confirms carrier selected → lock escrow (LOCKED)
    Sender marks delivered → mark_release_ready (RELEASE_READY)
    Admin confirms release / overrides → release_funds (RELEASED)
    Optional dispute → dispute calculation, partial refunds
    """

    @classmethod
    @db_transaction.atomic
    def create_escrow_for_offer(cls, offer, amount=None):
        """
        Create a new escrow for a given offer

        Args:
            offer: Offer instance the escrow is tied to.
            amount: Optional. If None, use offer.total_price.

        Returns:
            Escrow instance
        """
        if hasattr(offer, "escrow"):
            raise ValueError("Escrow already exists for this offer")
    
        if amount is None:
            amount = offer.total_price

        escrow = Escrow.objects.create(
            offer=offer,
            amount=amount,
            status=Escrow.Status.PENDING,
        )
        
        return escrow

    @classmethod
    @db_transaction.atomic
    def fund_escrow(cls, escrow: Escrow):
        """
        Debit sender wallet and mark escrow as FUNDED.
        """
        if escrow.status != Escrow.Status.PENDING:
            raise ValueError("Escrow must be pending to fund")

        sender_wallet = escrow.offer.sender.wallet
        if sender_wallet.balance < escrow.amount:
            raise ValueError("Insufficient balance in sender wallet")

        # Debit sender wallet
        sender_wallet.balance -= escrow.amount
        sender_wallet.save(update_fields=["balance"])

        # Create ledger entry
        WalletLedgerEntry.objects.create(
            wallet=sender_wallet,
            entry_type=WalletLedgerEntry.EntryType.DEBIT,
            amount=escrow.amount,
            note=f"Funding escrow {escrow.id}"
        )

        # Update escrow status
        escrow.status = Escrow.Status.FUNDED
        escrow.save(update_fields=["status"])
        return escrow

    @classmethod
    def lock_escrow(cls, escrow: Escrow):
        """
        Lock escrow funds.
        """
        if escrow.status != Escrow.Status.FUNDED:
            raise ValueError("Escrow must be funded first")
        escrow.status = Escrow.Status.LOCKED
        escrow.save(update_fields=["status"])
        return escrow

    @classmethod
    def mark_release_ready(cls, escrow: Escrow):
        """
        Mark escrow ready for release (sender marks delivered)
        """
        if escrow.status != Escrow.Status.LOCKED:
            raise ValueError("Escrow must be locked first")
        escrow.status = Escrow.Status.RELEASE_READY
        escrow.save(update_fields=["status"])
        return escrow

    @classmethod
    @db_transaction.atomic
    def release_funds(cls, escrow: Escrow,user):
        """
        Release escrow funds to carrier.
        Admin user is assigned to release the escrow.
        """
        if escrow.status != Escrow.Status.LOCKED:
            raise ValueError("Escrow must be locked first")
        
        # if escrow.status != Escrow.Status.RELEASE_READY:
        #     raise ValueError("Escrow not ready for release")
        
        # if not admin_user.is_staff:
        #     raise ValueError("Admin user required to release escrow and fund carrier wallet")

        carrier_wallet = escrow.offer.carrier.wallet
        carrier_wallet.balance += escrow.amount
        print(f"Carrier wallet balance before release: {carrier_wallet.balance}")
        carrier_wallet.save(update_fields=["balance"])

        WalletLedgerEntry.objects.create(
            wallet=carrier_wallet,
            entry_type=WalletLedgerEntry.EntryType.CREDIT,
            amount=escrow.amount,
            note=f"Released escrow {escrow.id}"
        )

        escrow.released_by = user
        escrow.status = Escrow.Status.RELEASED
        escrow.is_released = True
        escrow.released_at = timezone.now()
        escrow.save(update_fields=["status", "is_released", "released_at","released_by"])
    
        NotificationService.create(
            user=escrow.offer.carrier,
            type=Notification.Type.ESCROW_RELEASED,
            title="Escrow Released",
            message=f"Escrow {escrow.id} payment of {escrow.amount} has been released to you",
            content_object=escrow
        )
  
        return escrow

    @classmethod
    @db_transaction.atomic
    def cancel_escrow(cls, escrow: Escrow):
        """
        Cancel escrow and refund sender wallet.
        """
        if escrow.status in [Escrow.Status.RELEASED, Escrow.Status.DISPUTED]:
            raise ValueError("Cannot cancel released or disputed escrow")

        sender_wallet = escrow.offer.sender.wallet
        sender_wallet.balance += escrow.amount
        sender_wallet.save(update_fields=["balance"])

        WalletLedgerEntry.objects.create(
            wallet=sender_wallet,
            entry_type=WalletLedgerEntry.EntryType.CREDIT,
            amount=escrow.amount,
            note=f"Cancelled escrow {escrow.id}"
        )

        escrow.status = Escrow.Status.CANCELLED
        escrow.save(update_fields=["status"])
        return escrow

    @classmethod
    @db_transaction.atomic
    def dispute(cls, escrow: Escrow, release_amount_to_carrier: Decimal, admin_user, note=None):
        """
        Handle dispute settlement.
        release_amount_to_carrier is the portion paid to the carrier.
        Remaining is refunded to sender.
        """
        if escrow.status not in [Escrow.Status.LOCKED, Escrow.Status.RELEASE_READY]:
            raise ValueError("Only locked or ready escrow can be disputed")
        
        if not admin_user.is_staff:
            raise ValueError("Admin user required to dispute escrow")

        if not note:
            note = f"Dispute settlement for escrow {escrow.id}"
        sender_wallet = escrow.offer.sender.wallet
        carrier_wallet = escrow.offer.carrier.wallet

        # Credit carrier
        carrier_wallet.balance += release_amount_to_carrier
        carrier_wallet.save(update_fields=["balance"])

        WalletLedgerEntry.objects.create(
            wallet=carrier_wallet,
            entry_type=WalletLedgerEntry.EntryType.CREDIT,
            amount=release_amount_to_carrier,
            note=f"Dispute settlement for escrow {escrow.id}"
        )

        # Refund remaining to sender
        refund_amount = escrow.amount - release_amount_to_carrier
        sender_wallet.balance += refund_amount
        sender_wallet.save(update_fields=["balance"])
        WalletLedgerEntry.objects.create(
            wallet=sender_wallet,
            entry_type=WalletLedgerEntry.EntryType.CREDIT,
            amount=refund_amount,
            note=f"Dispute refund for escrow {escrow.id}"
        )

        # Assign admin user to disputed escrow
        escrow.released_by = admin_user
        escrow.status = Escrow.Status.DISPUTED
        escrow.note = note
        escrow.save(update_fields=["status","released_by","note"])
        return escrow