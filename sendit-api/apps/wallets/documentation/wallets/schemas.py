from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiTypes
from apps.wallets.serializers import WalletDashboardSerializer, WalletHistorySerializer
from .docs import WALLET_404_RESPONSE, WALLET_HISTORY_RESPONSE

# Extend schema
wallet_docs = extend_schema_view(
    list=extend_schema(
        summary='Retrieve wallet information',
        description='Returns the current user wallet details including balance, virtual account info, and available actions. User must be authenticated.',
        responses={
            200: WalletDashboardSerializer,
            404: OpenApiTypes.OBJECT
        },
        examples=[WALLET_404_RESPONSE],
        tags=['Wallets'],
    ),
    history=extend_schema(
        summary='Retrieve wallet transaction and ledger history',
        description='Returns paginated history of transactions and ledger entries for transparency. Includes date filtering, type, and status.',
        responses={200: WalletHistorySerializer},
        examples=[WALLET_HISTORY_RESPONSE],
        tags=['Wallets'],
    ),
)
