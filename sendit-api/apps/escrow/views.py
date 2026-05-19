from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import Escrow
from .serializers import EscrowSerializer
from .services.escrow_services import EscrowService 
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOfferOwnerOrIsAdmin
from .serializers import EscrowSerializer
from .documentation.escrow.schemas import  escrow_doc

@escrow_doc
class EscrowViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for viewing Escrows and triggering status transitions.
    - Fund: Fund the escrow
    -
    - Release: Release funds from the escrow (admin only)
    - Dispute: Open a dispute on the escrow (admin only) use the 
    release amount to carrie to specify the price to give the user. 
    the rest will be paid to the sender for the settlement.
    """
    help_text = "View all escrows or view a specific escrow by ID."
    queryset = Escrow.objects.select_related('offer', 'released_by').all()
    serializer_class = EscrowSerializer
    permission_classes = [IsAuthenticated] 

    @decorators.action(detail=True, permission_classes=[IsOfferOwnerOrIsAdmin], methods=['post'])
    def fund(self, request, pk=None):
        """
        Fund the escrow.
        """
        # Get the escrow instance
        escrow = self.get_object()
        print(f"offer owner:{escrow.offer.sender}")
        # Call your specific service method
        escrow= EscrowService.fund_escrow(escrow)
        return Response({"message": "Escrow funded successfully", "data":EscrowSerializer(escrow).data }, status=status.HTTP_200_OK)

    @decorators.action(detail=True, permission_classes=[IsOfferOwnerOrIsAdmin], methods=['post'])
    def release(self, request, pk=None):
        escrow = self.get_object()
        # Pass the admin user and any extra data (like partial release amount)
        amount = request.data.get('amount', escrow.amount)
        EscrowService.release_funds(escrow, user=request.user)
        return Response({"status": "Funds released"}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, permission_classes=[IsAdminUser], methods=['post'])
    def dispute(self, request, pk=None):
        escrow = self.get_object()

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["release_amount_to_carrier"]
        note = serializer.validated_data["note"]
        EscrowService.dispute(escrow, release_amount_to_carrier=amount, admin=request.user, note=note)
        return Response({"status": "Dispute marked"}, status=status.HTTP_200_OK)
