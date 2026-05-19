from apps.core.services.notification_service import NotificationService
from apps.account.models import Profile as UserProfile
from apps.core.services.geo_service import GeoService
from apps.core.models import Notification

class OfferService:
    """
    Service to handle offer lifecycle events and carrier matching.
    """
    DEFAULT_RADIUS_KM = 10

    # -------------------------
    # 🔍 MATCHING: CARRIERS
    # -------------------------

    @classmethod
    def get_nearby_carriers(cls, pickup_location):
        """
        Finds carriers within the default radius of a pickup location.
        """
        # OPTIMIZATION: Only pull profiles that have a location and are 'carrier' type
        # This prevents looping through thousands of non-carrier or empty profiles.
        profiles = UserProfile.objects.select_related("user", "location").filter(
            location__isnull=False,
            type__iexact="carrier" # Case-insensitive match at DB level
        )
        
        nearby = []

        if not pickup_location:
            print("[offerservices]: Error - No pickup location provided for matching.")
            return []

        for profile in profiles:
            # DEFENSIVE: Double check location exists before accessing lat/lng
            if not profile.location or profile.location.latitude is None:
                continue
            
            # Safe logging: Latitude/Longitude are now guaranteed to exist here
            print(f"[offerservices]: Checking carrier {profile.user.email} at "
                  f"({profile.location.latitude}, {profile.location.longitude})")

            distance = GeoService.distance_between_locations(
                pickup_location,
                profile.location
            )

            # Check if within radius (10km default)
            if distance is not None and distance <= cls.DEFAULT_RADIUS_KM:
                nearby.append(profile.user)

        print(f"[offerservices]: Found {len(nearby)} nearby carriers for offer.")
        return nearby

    # -------------------------
    # 🔍 MATCHING: OFFERS (For Marketplace filtering)
    # -------------------------

    @classmethod
    def get_nearby_offers(cls, offers, user_location, radius_km=10):
        nearby = []
        for offer in offers:
            loc = offer.pickup_location
            if not loc or not user_location:
                continue

            distance = GeoService.distance_between_locations(user_location, loc)

            if distance is not None and distance <= radius_km:
                offer.distance = distance
                nearby.append(offer)

        return sorted(nearby, key=lambda x: x.distance)

    # -------------------------
    # 🔔 EVENT: OFFER POSTED
    # -------------------------

    @classmethod
    def handle_offer_posted(cls, offer):
        """
        Triggered when an offer status changes to POSTED.
        Identifies nearby carriers and sends bulk notifications.
        """
        # Ensure we have a valid pickup point to calculate from
        if not offer.pickup_location:
            print(f"[offerservices]: Skipping notifications for {offer.code} - No pickup location.")
            return

        print(f"[offerservices]: handle_offer_posted for {offer.code} "
              f"at ({offer.pickup_location.latitude}, {offer.pickup_location.longitude})")
        
        carriers = cls.get_nearby_carriers(offer.pickup_location)

        if not carriers:
            print(f"[offerservices]: No nearby carriers found for {offer.code}.")
            return

        # Prepare bulk notification data
        notification_data = [
            {
                "user": carrier,
                "type": Notification.Type.NEW_OFFER,
                "title": "New Delivery Nearby",
                "message": f"Package {offer.code} is available for pickup near you.",
                "content_object": offer
            }
            for carrier in carriers
        ]

        # Use the specialized bulk service to minimize DB hits
        try:
            NotificationService.bulk_create(notification_data)
            print(f"[offerservices]: Successfully notified {len(carriers)} carriers.")
        except Exception as e:
            # We catch this so a notification failure doesn't rollback the whole Offer Post
            print(f"[offerservices]: Notification bulk_create failed: {str(e)}")

    # -------------------------
    # 🔔 EVENT: PROPOSAL HANDLERS
    # -------------------------

    @staticmethod
    def handle_new_proposal(proposal):
        offer = proposal.offer
        NotificationService.create(
            user=offer.sender,
            type=Notification.Type.NEW_PROPOSAL,
            title="New Delivery Proposal",
            message=f"A carrier applied for {offer.code}",
            content_object=offer
        )

    @staticmethod
    def handle_proposal_accepted(proposal):
        NotificationService.create(
            user=proposal.carrier,
            type=Notification.Type.PROPOSAL_ACCEPTED,
            title="You Got the Job 🎉",
            message=f"You were selected for offer code: {proposal.offer.code}",
            content_object=proposal.offer
        )

    @staticmethod
    def handle_proposal_rejected(proposal):
        NotificationService.create(
            user=proposal.carrier,
            type=Notification.Type.PROPOSAL_REJECTED,
            title="Proposal Rejected",
            message=f"You were rejected for {proposal.offer.code}",
            content_object=proposal.offer
        )

    @staticmethod
    def handle_offer_accepted(offer):
        if not offer.carrier:
            return

        NotificationService.create(
            user=offer.carrier,
            type=Notification.Type.PROPOSAL_ACCEPTED,
            title="You Got the Job 🎉",
            message=f"You were selected for {offer.code}",
            content_object=offer
        )