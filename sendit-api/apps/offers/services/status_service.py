from django.db import transaction
from rest_framework.exceptions import ValidationError
from ..models import Offer
from .offer_service import OfferService
from apps.escrow.services.escrow_services import EscrowService

class OfferStatusService:
    """
     ALLOWED_TRANSITIONS = {
    "draft": ["posted"],
    "posted": ["accepted", "cancelled"],
    "accepted": ["in_transit", "cancelled"],
    "in_transit": ["delivered"],
}
    """

    @classmethod
    def transition(cls, offer, action, user):

        if action == Offer.Status.POSTED:
            return cls._post(offer, user)

        if action == Offer.Status.ACCEPTED:
            return cls._accept(offer, user)

        if action == Offer.Status.IN_TRANSIT:
            return cls._start_transit(offer, user)

        if action == Offer.Status.DELIVERED:
            return cls._deliver(offer, user)

        if action == Offer.Status.CANCELLED:
            return cls._cancel(offer, user)

        if action == Offer.Status.DISPUTED:
            return cls._dispute(offer, user)

        raise ValidationError("Invalid action")

    @staticmethod
    def _post(offer, user):

        if offer.sender != user:
            raise ValidationError("Not your offer")

        if offer.status != Offer.Status.DRAFT:
            raise ValidationError("Only draft can be posted")

        offer.status = Offer.Status.POSTED
        offer.current_step = Offer.Step.POSTED
        offer.is_complete()
        offer.save()
        EscrowService.create_escrow_for_offer(offer)


        OfferService.handle_offer_posted(offer)

        return offer

    @staticmethod
    def _accept(offer, user):

        if getattr(user, "type", None) != "carrier":
            raise ValidationError("Only carriers can accept")

        with transaction.atomic():
            offer = Offer.objects.select_for_update().get(pk=offer.pk)

            if offer.status != Offer.Status.POSTED:
                raise ValidationError("Offer not available")

            if offer.carrier:
                raise ValidationError("Offer already accepted")

            offer.carrier = user
            offer.status = Offer.Status.ACCEPTED
            offer.save()

        OfferService.handle_offer_accepted(offer)

        return offer

    @staticmethod
    def _start_transit(offer, user):
        "sender can tell the offer is on transit"
        if offer.sender.email != user.email and offer.carrier != user.email:
            print(f"offer in transit:{offer.sender, offer.carrier, user}")
            raise ValidationError("Not your delivery")

        if offer.status != Offer.Status.ACCEPTED:
            raise ValidationError("Invalid state")

        offer.status = Offer.Status.IN_TRANSIT
        offer.save()
        EscrowService.lock_escrow(offer.escrow)

        return offer

    @staticmethod
    def _deliver(offer, user):
        if offer.sender.email != user.email:
            raise ValidationError("Not your delivery")

        if offer.status != Offer.Status.IN_TRANSIT:
            raise ValidationError("Invalid state")

        with transaction.atomic():
            offer.status = Offer.Status.DELIVERED
            offer.save()

            # Mark escrow as ready for release
            try:
                # EscrowService.mark_release_ready(offer.escrow)
                EscrowService.release_funds(offer.escrow,user)
            except Exception as e:
                # Log that escrow couldn't be updated
                print(
                    f"Error updating escrow status for offer {offer.code}: {e}")

        return offer

    @staticmethod
    def _cancel(offer, user):

        if offer.sender != user:
            raise ValidationError("Only sender can cancel")

        if offer.status not in [
            Offer.Status.POSTED,
            Offer.Status.ACCEPTED
        ]:
            raise ValidationError("Cannot cancel at this stage")

        offer.status = Offer.Status.CANCELLED
        offer.save()

        return offer

    @staticmethod
    def _dispute(offer, user):
        if user not in [offer.sender, offer.carrier]:
            raise ValidationError("Only sender or carrier can dispute")

        if offer.status not in [Offer.Status.ACCEPTED, Offer.Status.IN_TRANSIT, Offer.Status.DELIVERED]:
            raise ValidationError("Cannot dispute at this stage")

        with transaction.atomic():
            offer.status = Offer.Status.DISPUTED
            offer.save()

            try:
                escrow = offer.escrow
                escrow.dispute()
            except Exception as e:
                print(f"Error updating escrow for dispute: {e}")

        return offer
