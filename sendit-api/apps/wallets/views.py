from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Wallet
from .serializers import WalletDashboardSerializer, WalletHistorySerializer
from .services.wallet_services import WalletService
from .utils import apply_date_filter, WalletHistoryPagination
from .documentation.wallets.schemas import wallet_docs

@wallet_docs
class WalletViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user):
        wallet, _ = Wallet.objects.get_or_create(user=user)
        return wallet

    # ✅ GET /wallet/
    def list(self, request):
        wallet = self.get_object(request.user)
        serializer = WalletDashboardSerializer(
            wallet,
            context={"request": request}
        )
        return Response(data={"message": "retrieved successfully", "data": serializer.data}, status=200)

    # ✅ GET /wallet/history/

    @action(detail=False, methods=["get"])
    def history(self, request):
        """
        history
        """
        wallet = request.user.wallet
        qs = apply_date_filter(wallet, request)
        print(f"wallet wallet{wallet} qs{qs}")

        data = WalletService.get_full_history(qs)

        # pagination
        paginator = WalletHistoryPagination()
        page = paginator.paginate_queryset(data, request)

        serializer = WalletHistorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

  # # ✅ POST /wallet/withdraw/
  #   @action(detail=False, methods=["post"])
  #   def withdraw(self, request):
  #       amount = request.data.get("amount")

  #       return Response({
  #           "message": "Withdrawal request received",
  #           "amount": amount
  #       }, status=status.HTTP_200_OK)
