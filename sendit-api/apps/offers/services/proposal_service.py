from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.offers.models import Offer, Proposal
from apps.escrow.models import Escrow
from apps.escrow.services.escrow_services import EscrowService
from .offer_service import OfferService

class ProposalService:
    @staticmethod
    @transaction.atomic
    def create_proposal(offer: Offer, carrier, price, message=""):
        """
        Carrier bids for an offer.
        Initial status: PENDING
        """
        # Check if the user is a carrier
        if getattr(carrier.profile, "type", None) != "carrier":
            raise ValidationError("Only carriers can bid for offers")
        
        # Check if user is verified
        if not carrier.profile.is_verified:
            raise ValidationError("Your profile must be verified to bid")

        # Check if offer is posted
        if offer.status != Offer.Status.POSTED:
            raise ValidationError("This offer is no longer accepting proposals")

        # Check if carrier already bid
        if Proposal.objects.filter(offer=offer, carrier=carrier).exists():
            raise ValidationError("You have already submitted a proposal for this offer")

        proposal = Proposal.objects.create(
            offer=offer,
            carrier=carrier,
            price=price,
            message=message,
            status=Proposal.Status.PENDING
        )

        # Notify sender
        OfferService.handle_new_proposal(proposal)
        return proposal

    @staticmethod
    @transaction.atomic
    def accept_proposal(proposal: Proposal, user):
        """
        Sender accepts a carrier's proposal.
        - Selected proposal -> ACCEPTED
        - Other proposals -> REJECTED
        - Offer -> ACCEPTED and carrier attached
        - Escrow status -> INITIATED (funds are now tied to this specific carrier)
        """
        with transaction.atomic():

            # 🔒 Lock the offer row (prevents race conditions)
            offer = proposal.offer.__class__.objects.select_for_update().get(id=proposal.offer.id)

            # ✅ Authorization
            if offer.sender != user:
                raise ValidationError("You are not authorized to accept this proposal")

            # ✅ Proposal must still be pending
            if proposal.status != Proposal.Status.PENDING:
                raise ValidationError("This proposal is not pending")

            # ✅ Offer must not already be accepted
            if offer.status == Offer.Status.ACCEPTED:
                raise ValidationError("This offer has already been accepted")

            # ✅ Ensure no escrow exists
            if Escrow.objects.filter(offer=offer).exists():
                raise ValidationError("Escrow already exists for this offer")

            # =========================
            # ✅ STATE TRANSITIONS
            # =========================
            # Accept this proposal
            proposal.status = Proposal.Status.ACCEPTED
            proposal.save()

            # Reject others
            Proposal.objects.filter(offer=offer).exclude(id=proposal.id).update(
                status=Proposal.Status.REJECTED
            )

            # Update offer
            offer.carrier = proposal.carrier
            offer.status = Offer.Status.ACCEPTED
            offer.save()

            # Create escrow AFTER state is consistent
            price = getattr(proposal, "price", 0) if proposal else 0
            EscrowService.create_escrow_for_offer(offer,amount=price)

        OfferService.handle_proposal_accepted(proposal)

        return proposal
    
    def reject_proposal(proposal: Proposal, user):
        """
        Sender rejects a carrier's proposal.
        - Proposal -> REJECTED
        """
        # Check if the user is the sender of the offer
        if proposal.offer.sender != user:
            raise ValidationError("You are not authorized to reject this proposal")

        # Update proposal status
        proposal.status = Proposal.Status.REJECTED
        proposal.save()

        # Notify carrier
        OfferService.handle_proposal_rejected(proposal)
        return proposal
