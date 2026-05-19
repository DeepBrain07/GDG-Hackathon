
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied,  ValidationError
from .permissions import IsOfferOrProposalOwnerOrAdmin

from .models import Offer, Proposal
from .services.step_service import OfferStepService
from apps.offers.services.offer_service import OfferService
from apps.offers.services.status_service import OfferStatusService
from apps.offers.services.proposal_service import ProposalService
from apps.payments.services.payment_service import PaymentService
from .serializers import  (OfferCreateSerializer, OfferListSerializer,
OfferDetailsSerializer,OfferLocationSerializer, OfferUpdateSerializer,OfferPricingSerializer, 
OfferTransitionSerializer,OfferSerializer, ProposalSerializer, ProposalListSerializer, ProposalStatusSerializer)
from .documentation.offers.schemas import (offer_list_create_doc, offer_step_details_doc, offer_location_doc, 
                                           offer_pricing_doc, offer_review_doc, offer_transition_doc, offer_detail_doc, proposal_doc)

from .permissions import IsSender

@offer_list_create_doc
class OfferListCreateView(ListCreateAPIView):
    """
    you can see posted offer in the market
    you can see your own offer in the market whe you filter ?mine=true
    """
    # queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def get_queryset(self):
        queryset = Offer.objects.select_related(
            "sender",
            "carrier",
            "pickup_location",
            "delivery_location",
        ).prefetch_related(
            "media",
        )
        params = self.request.query_params
        print(f"[offer list] queryset: {queryset}, params: {params}")

         # 1. Robust Boolean Check
        mine = str(params.get("mine", "")).lower() in ["1", "true", "yes"]

        if mine:
            # User wants their own offers (regardless of status)
            queryset = queryset.filter(sender=self.request.user)
        else:
            # Marketplace view: only show public/posted offers 
            # AND exclude the user's own offers so they don't see themselves in the market
            queryset = queryset.filter(status=Offer.Status.POSTED).exclude(sender=self.request.user)

        # -------------------------------
        # Filter: urgent
        # -------------------------------
        urgent = params.get("urgent")
        if urgent is not None:
            if urgent.lower() in ["1", "true", "yes"]:
                queryset = queryset.filter(is_urgent=True)
            elif urgent.lower() in ["0", "false", "no"]:
                queryset = queryset.filter(is_urgent=False)

        # -------------------------------
        # Filter: price range
        # -------------------------------
        min_price = params.get("min_price")
        max_price = params.get("max_price")

        if min_price:
            try:
                queryset = queryset.filter(total_price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(total_price__lte=float(max_price))
            except ValueError:
                pass

        # -------------------------------
        # Filter: today
        # -------------------------------
        today = params.get("today")
        if today and today.lower() in ["1", "true", "yes"]:
            start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            queryset = queryset.filter(created_at__range=(start, end))

        # -------------------------------
        # Filter: city or area
        # -------------------------------
        city_or_area = params.get("city_or_area")
        if city_or_area:
            queryset = queryset.filter(
                Q(pickup_location__city__icontains=city_or_area) |
                Q(pickup_location__area__icontains=city_or_area) |
                Q(delivery_location__city__icontains=city_or_area) |
                Q(delivery_location__area__icontains=city_or_area)
            )

        # -------------------------------
        # Filter: nearby (chained)
        # -------------------------------
        lat = params.get("lat")
        lng = params.get("lng")
        radius = params.get("radius", 10)  # default 10 km

        if lat and lng:
            try:
                user_location = OfferService.create_temp_location(float(lat), float(lng))
                queryset = OfferService.get_nearby_offers(offers=queryset, user_location=self.request.user.profile.location, radius_km=float(radius) if radius else 10)
            except ValueError:
                pass

        return queryset.order_by("-created_at")

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        print(f"[offer list] queryset: {queryset}")

        if not queryset.exists():
            return Response({
                "count": 0,
                "message": "No offers match found",
                "offers": []
            }, status=200)

        # Use serializer with many=True
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "count": queryset.count(),
            "offers": serializer.data
        }, status=200)

    def create(self, request, *args, **kwargs):
        """Create a new offer"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            offer = serializer.save()

            return Response({
                "success": True,
                "message": "STEP_CREATE_SUCCESS",
                "data": {
                    "id": offer.id,
                    "status": offer.status,
                    "current_step": offer.current_step
                }
            })

        except ValidationError as e:
            return Response({
                "success": False,
                "error": {
                    "code": "STEP_VALIDATION_FAILED",
                    "message": str(e)
                }
            }, status=400)

class BaseOfferStepView(APIView):
    permission_classes = [IsAuthenticated]

    step = None
    serializer_class = None

    def get(self, request, pk):
        """Return the serializer fields for browsable form"""
        offer = get_object_or_404(Offer, pk=pk, sender=request.user)
        serializer = self.serializer_class(instance=offer)
        return Response(serializer.data)

    def patch(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk, sender=request.user)

        serializer = self.serializer_class(instance=offer,data=request.data,partial=True,context={"request": request})
        serializer.is_valid(raise_exception=True)

        try:
            print(f"[base step] step: {self.step} id{offer.id}, status{offer.current_step}")
            offer = OfferStepService.update_step(
                offer=offer,
                step=self.step,
                data=serializer.validated_data,
                user=request.user
            )

            return Response({
                "success": True,
                "message": "STEP_UPDATE_SUCCESS",
                "data": OfferListSerializer(offer).data
                
            })

        except ValidationError as e:
            return Response({
                "success": False,
                "error": {
                    "code": "STEP_VALIDATION_FAILED",
                    "message": str(e)
                }
            }, status=400)

@offer_step_details_doc
class OfferDetailsView(BaseOfferStepView):
    step = Offer.Step.DETAILS
    serializer_class = OfferDetailsSerializer

@offer_location_doc
class OfferLocationView(BaseOfferStepView):
    step = Offer.Step.LOCATION
    serializer_class = OfferLocationSerializer

@offer_pricing_doc
class OfferPricingView(BaseOfferStepView):
    step = Offer.Step.PRICING
    serializer_class = OfferPricingSerializer

@offer_review_doc
class OfferReviewView(BaseOfferStepView):
    """
    offer review both path and update skipping the step:

    {
    "package_type": "large",
    "is_fragile": false,
    "pickup_location": {
    
        "city": "Ogbomosho",
        "area": "Under-G",
        "street": "LAUTECH Main Road",
        "landmark": "LAUTECH Second Gate",
        "latitude": 8.1229,
        "longitude": 4.2480
    },
    "pickup_time": "2023-12-12T10:00:00",
    "delivery_location": {
    
        "city": "Ibadan",
        "area": "Iwo Road",
        "street": "Iwo Road Interchange",
        "landmark": "Iwo Road Roundabout / Motor Park",
        "latitude": 7.3971,
        "longitude": 3.9402
    },
    "is_urgent": false,
    "base_price": 5000.0,
    "receiver_name": "Akinwale Bobo",
    "receiver_phone": "08033145678"
}   
    """
    permission_classes = [IsSender]
    step = Offer.Step.REVIEW
    serializer_class = OfferUpdateSerializer

    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk, sender=request.user)

        if offer.sender != request.user:
            raise PermissionDenied()

        serializer = OfferListSerializer(offer)

        return Response({
            "success": True,
            "data": serializer.data
        })


@offer_transition_doc
class OfferTransitionView(APIView):
    """offer transition: action posted,accept,reject,cancel
    The offer lifecyle trnsition 
    - posted: The offer is posted and is now available for proposal.
    - accept: The offer is accepted by the carrier(only after proposal).
    - in_transit: The offer is in transit.
    - delivered: The offer is delivered.
    - cancelled: The offer is cancelled by the sender.
    - reject: The offer is rejected by the carrier.
    - cancel: The offer is cancelled by the sender.
    """
    permission_classes = [IsSender]

    def post(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        serializer = OfferTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            OfferStatusService.transition(
              offer=offer,
              action=str(serializer.validated_data["action"]).lower().strip(),
              user=request.user
            )

            return Response({
              "success": True,
              "message":"OFFER STATUS UPDATE SUCCESS",
              "data": {
                  "id": offer.id,
                  "status": offer.status,
                  "current_step": offer.current_step
              }
          },status=200)

        except Exception as e:
            return Response({
                "error": True,
                "message": str(e)
            }, status=400)



@offer_detail_doc
class OfferView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        serializer = OfferSerializer(offer)

        return Response({
            "success": True,
            "data": serializer.data
        })
    

@proposal_doc
class ProposalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Proposal management
    - Carriers can create proposals for posted offers
    - Senders can see proposals for their offers
    - Senders can accept a proposal (it rejects for other automatically)
    - Senders can reject a proposal
    """

    http_method_names = ["get", "post", "patch"]
    permission_classes = [IsOfferOrProposalOwnerOrAdmin]
    serializer_class = ProposalListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ProposalListSerializer
        return ProposalSerializer

    def get_queryset(self):
        user = self.request.user
        # Senders see proposals for their offers
        # Carriers see their own proposals
        return Proposal.objects.filter(
            Q(offer__sender=user) | Q(carrier=user)
        ).select_related("offer", "carrier", "carrier__profile")

    def create(self, request, *args, **kwargs):
        """
        Carrier bids for an offer
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        offer = serializer.validated_data["offer"]

        try:
            proposal = ProposalService.create_proposal(
                offer=offer,
                carrier=request.user,
                price=serializer.validated_data.get("price")
            )
            return Response(ProposalListSerializer(proposal).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        """
        Sender accepts a carrier's proposal
        - The proposal status is updated to ACCEPTED
        - The offer status is updated to ACCEPTED
        - The escrow is created and the offer is attached to the escrow
        """
        proposal = self.get_object()

        try:
            proposal = ProposalService.accept_proposal(proposal, request.user)
            return Response({"message": "Proposal accepted successfully", 
                             "data": {"proposal_id": proposal.id,"escrow_id": proposal.offer.escrow.id,
                                       "amount": proposal.offer.escrow.amount}}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """
        Sender rejects a carrier's proposal
        """
        proposal = self.get_object()
        try:
            ProposalService.reject_proposal(proposal, request.user)
            return Response({"message": "Proposal rejected successfully"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


