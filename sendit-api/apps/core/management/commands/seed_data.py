import random
import string
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal

# Initialize the manual generator
fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'account.CustomUser'

    email = factory.Sequence(lambda n: f"user{n}@sendit.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("user_name") # Added for __str__ methods
    is_active = True
    agree_to_privacy_policy = True

class Command(BaseCommand):
    help = "Seeds the Sendit database with Users, Profiles, Wallets, and now Chats/Notifications."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # 1. Lazy Imports
        from django.contrib.auth import get_user_model
        from apps.account.models import Profile, Verification
        from apps.offers.models import Offer, Proposal
        from apps.wallets.models import Wallet, WalletLedgerEntry
        from apps.payments.models import Transaction
        from apps.core.models import Location, Notification, ChatRoom, Message
        from apps.core.services.notification_service import NotificationService
        
        User = get_user_model()
        SEED_PASSWORD = "Sendit_Secure_Auth_2026!"

        self.stdout.write(self.style.MIGRATE_LABEL("--- Starting Seeding Process ---"))

        # ... (Keep your PROTECTED_EMAILS and Cleanup logic the same) ...
        PROTECTED_EMAILS = [
            "heritage@example.com", 
            "olusatimmie07@gmail.com",
            "deepbrain77@gmail.com"
        ]

        # 4. Create Locations (Keep existing)
        # 5. Helper Function to Seed Wallet (Keep existing)
        # 6. Seed Protected Users (Keep existing)
        # 7. Seed 10 Random Users (Keep existing)

        # ---------------------------------------------------------
        # 8. Seed Offers, Notifications, and Chats
        # ---------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_LABEL("\n--- Seeding Offers, Notifications, and Chats ---"))
        
        all_users = list(User.objects.all())
        locations = list(Location.objects.all())

        for i in range(15):  # Create 15 sample offers
            sender = random.choice(all_users)
            pickup = random.choice(locations)
            delivery = random.choice(locations)
            
            # Create Offer
            offer = Offer.objects.create(
                sender=sender,
                package_type=random.choice(['small', 'medium', 'large']),
                base_price=Decimal(random.randint(2000, 10000)),
                pickup_location=pickup,
                delivery_location=delivery,
                status=Offer.Status.POSTED,
                current_step=Offer.Step.POSTED,
                description=fake.sentence(),
                receiver_name=fake.name(),
                receiver_phone=fake.phone_number()
            )

            # 8b. Create a Proposal and a Chat for some offers
            if i % 2 == 0:
                carrier = random.choice([u for u in all_users if u != sender])
                proposal = Proposal.objects.create(
                    offer=offer,
                    carrier=carrier,
                    price=offer.base_price,
                    message="I can deliver this today!",
                    status=Proposal.Status.PENDING
                )

                # Notify sender about the proposal (ONLY notifications relating to proposals)
                NotificationService.create(
                    user=sender,
                    type=Notification.Type.NEW_PROPOSAL,
                    title="New Proposal",
                    message=f"{carrier.first_name} sent a bid for {offer.code}",
                    content_object=proposal
                )

                # 8c. Seed Chat Room and Messages
                # Note: ChatRoom has a OneToOneField to Offer
                room = ChatRoom.objects.create(offer=offer)
                room.participants.add(sender, carrier)

                # Seed a conversation
                conv_lines = [
                    (carrier, "Hello! I saw your offer. Is the package ready for pickup?"),
                    (sender, "Yes, it is. It's quite fragile though, please be careful."),
                    (carrier, "No problem. I have padding in my vehicle."),
                    (sender, "Great, see you soon.")
                ]

                # 8c. Seed Chat Room and Messages
                for speaker, text in conv_lines:
                    Message.objects.create(
                        room=room,
                        sender=speaker,
                        text=text,
                        timestamp=timezone.now() - timezone.timedelta(minutes=random.randint(1, 60))
                    )

        self.stdout.write(self.style.SUCCESS(f"\n✅ Seeded {Offer.objects.count()} Offers, {Notification.objects.count()} Notifications (Proposals only), and {ChatRoom.objects.count()} Chat Rooms."))