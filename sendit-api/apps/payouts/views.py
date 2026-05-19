from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.payouts.models import Payout
from apps.payouts.serializers import PayoutSerializer
from apps.payouts.services.payout_service import PayoutService
from apps.offers.models import Offer

class PayoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payout management.
    - Admins can trigger payouts for delivered offers.
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer

    @action(detail=False, methods=["post"], url_path="release")
    def release_funds(self, request):
        offer_id = request.data.get("offer_id")
        if not offer_id:
            return Response({"error": "offer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            offer = Offer.objects.get(id=offer_id)
            payout = PayoutService.release_funds(offer)
            return Response(PayoutSerializer(payout).data, status=status.HTTP_200_OK)
        except Offer.DoesNotExist:
            return Response({"error": "Offer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


