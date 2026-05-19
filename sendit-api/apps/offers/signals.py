from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Proposal
from apps.core.services.notification_service import NotificationService 

@receiver(post_save, sender=Proposal)
def handle_proposal_notifications(sender, instance, created, **kwargs):
    """
    Handles notifications for Proposal lifecycle:
    1. New Bid: Notify the Offer Sender
    2. Bid Accepted: Notify the Carrier
    3. Bid Rejected: Notify the Carrier
    """
    if created:
        # Carrier just placed a bid -> Notify the Sender
        NotificationService.create(
            user=instance.offer.sender,
            type="NEW_BID",
            title="New Bid Received!",
            message=f"{instance.carrier.get_full_name()} offered ₦{instance.price:,} for your delivery.",
            content_object=instance
        )
    else:
        # Check for status changes (Accepted/Rejected)
        # Assuming your model tracks status changes
        if instance.status == "ACCEPTED":
            NotificationService.create(
                user=instance.carrier,
                type="BID_ACCEPTED",
                title="Bid Accepted! 🚀",
                message=f"Your bid for delivery to {instance.offer.delivery_location.city} was accepted.",
                content_object=instance
            )
        elif instance.status == "REJECTED":
            NotificationService.create(
                user=instance.carrier,
                type="BID_REJECTED",
                title="Bid Update",
                message=f"Your bid for the offer from {instance.offer.pickup_location.city} was declined.",
                content_object=instance
            )