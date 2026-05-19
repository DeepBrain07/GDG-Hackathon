from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample, OpenApiTypes
from .docs import ESCROW_FUND_RESPONSE, ESCROW_RELEASE_REQUEST, ESCROW_RELEASE_RESPONSE, ESCROW_DISPUTE_REQUEST, ESCROW_DISPUTE_RESPONSE
from apps.escrow.serializers import EscrowSerializer


escrow_doc = extend_schema_view(
    list=extend_schema(
        summary='List Escrows',
        description='Retrieve all escrows accessible to the authenticated user.',
        responses={200: EscrowSerializer},
        tags=['Escrow'],
    ),
    retrieve=extend_schema(
        summary='Retrieve Escrow',
        description='Retrieve a specific escrow by ID.',
        responses={200: EscrowSerializer},
        tags=['Escrow'],
    ),
    fund=extend_schema(
        summary='Fund Escrow',
        description='Fund an escrow after a proposal has been accepted.',
        responses={200: OpenApiTypes.OBJECT},
        examples=[ESCROW_FUND_RESPONSE],
        tags=['Escrow'],
    ),
    release=extend_schema(
        summary='Release Escrow (Admin Only)',
        description=(
            "Release funds from escrow to carrier wallet.\n\n"
            "Rules:\n"
            "- Only admin can perform this action\n"
            "- Escrow must be in RELEASE_READY state\n"
            "- Amount defaults to full escrow amount if not provided"
        ),
        request=OpenApiTypes.OBJECT,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[ESCROW_RELEASE_REQUEST, ESCROW_RELEASE_RESPONSE],
        tags=['Escrow'],
    ),
    dispute=extend_schema(
        summary='Dispute Escrow (Admin Only)',
        description=(
            "Resolve an escrow dispute by splitting funds between carrier and sender.\n\n"
            "STRICT RULES:\n"
            "1. release_amount_to_carrier is REQUIRED\n"
            "2. note is REQUIRED\n"
            "3. release_amount_to_carrier <= escrow.amount\n\n"
            "FUND FLOW:\n"
            "- Carrier receives: release_amount_to_carrier\n"
            "- Sender receives: (escrow.amount - release_amount_to_carrier)\n"
        ),
        request=OpenApiTypes.OBJECT,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[ESCROW_DISPUTE_REQUEST, ESCROW_DISPUTE_RESPONSE],
        tags=['Escrow'],
    ),
)