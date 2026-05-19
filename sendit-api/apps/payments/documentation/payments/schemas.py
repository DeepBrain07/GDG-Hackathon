from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiTypes

from apps.payments.serializers import WebFundingPayloadSerializer
from .docs import WEB_FUNDING_200_RESPONSE, WEB_FUNDING_400_RESPONSE, WEB_FUNDING_REQUEST
# -----------------------------
# Schema for the WebFundingPayloadView
# -----------------------------
web_funding_create_payload_doc = extend_schema_view(
    post=extend_schema(
        summary="To Initiate wallet funding via web without these details i won't be able to track the transaction.",
        description=(
            "Creates a wallet funding transaction in INITIATED status and returns a payload "
            "that can be used by the frontend to render an inline payment form. "
            "User must be authenticated."
        ),
        request=WebFundingPayloadSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[WEB_FUNDING_200_RESPONSE, WEB_FUNDING_400_RESPONSE],
        tags=['Wallets'],
    ),
)
web_funding_upload_payload_doc = extend_schema_view(
    post=extend_schema(
        summary="To Initiate wallet funding via web without these details i won't be able to track the transaction.",
        description=(
            "Creates a wallet funding transaction in INITIATED status and returns a payload "
            "that can be used by the frontend to render an inline payment form. "
            "User must be authenticated."
        ),
        
        request=WEB_FUNDING_REQUEST,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[WEB_FUNDING_REQUEST,WEB_FUNDING_200_RESPONSE, WEB_FUNDING_400_RESPONSE],
        tags=['Wallets'],
    ),
)
