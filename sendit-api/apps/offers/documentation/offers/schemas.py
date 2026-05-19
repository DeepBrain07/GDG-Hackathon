from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.types import OpenApiTypes
from .docstrings import (OFFERS_EMPTY_RESPONSE, OFFERS_LIST_RESPONSE,OFFER_UPDATE_RESPONSE,
                         OFFER_STEP_ERROR_RESPONSE, OFFER_REVIEW_RESPONSE, OFFER_TRANSITION_ERROR, 
                         PROPOSAL_CREATE_REQUEST, PROPOSAL_ACCEPT_RESPONSE, PROPOSAL_REJECT_RESPONSE,
                         OFFER_TRANSITION_REQUEST, OFFER_TRANSITION_SUCCESS, PROPOSAL_CREATE_FAILED_RESPONSE
)
from apps.offers.serializers import  (OfferCreateSerializer, OfferListSerializer,
OfferDetailsSerializer,OfferLocationSerializer,OfferPricingSerializer, OfferUpdateSerializer,
OfferTransitionSerializer, OfferSerializer, ProposalSerializer)

"""
offer status view : https://chatgpt.com/s/t_69c048767d148191ba8d24822cd74fcc
documentation: https://chatgpt.com/s/t_69c047fecc548191ba7fcca54885ade7
filteing base list endpoint: https://chatgpt.com/s/t_69c048334590819188b0a94c939002fc
"""

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

offer_list_create_doc = extend_schema_view(
    get=extend_schema(
        summary="List Offers",
        description=(
            "Retrieve a list of offers. You can filter offers using query parameters "
            "such as mine, urgent, today, price ranges, nearby locations, city, and area."
            "`mine=True` default setting to see all your offer event those not already review and posted"
            "`Example: /offers/?mine=True&urgent=True&price_min=100&price_max=500&lat=37.7749&lng=-122.4194&radius_km=5``"
        ),
        parameters=[
            OpenApiParameter(
                name="mine",
                type=OpenApiTypes.BOOL,
                description="Return only offers created by the authenticated user",
                required=False
            ),
            OpenApiParameter(
                name="urgent",
                type=OpenApiTypes.BOOL,
                description="Filter only urgent offers",
                required=False
            ),
            OpenApiParameter(
                name="today",
                type=OpenApiTypes.BOOL,
                description="Filter offers created today",
                required=False
            ),
            OpenApiParameter(
                name="price_min",
                type=OpenApiTypes.NUMBER,
                description="Minimum total price filter",
                required=False
            ),
            OpenApiParameter(
                name="price_max",
                type=OpenApiTypes.NUMBER,
                description="Maximum total price filter",
                required=False
            ),
            OpenApiParameter(
                name="lat",
                type=OpenApiTypes.FLOAT,
                description="Latitude for nearby offers filter",
                required=False
            ),
            OpenApiParameter(
                name="lng",
                type=OpenApiTypes.FLOAT,
                description="Longitude for nearby offers filter",
                required=False
            ),
            OpenApiParameter(
                name="radius_km",
                type=OpenApiTypes.NUMBER,
                description="Radius in km for nearby offers filter (default 10km)",
                required=False
            ),
            OpenApiParameter(
                name="city",
                type=OpenApiTypes.STR,
                description="Filter offers by pickup location city",
                required=False
            ),
            OpenApiParameter(
                name="area",
                type=OpenApiTypes.STR,
                description="Filter offers by pickup location area",
                required=False
            ),
        ],
        responses={200: OfferListSerializer(many=True)},
        tags=["Offers"]
    ),
    post=extend_schema(
        summary="Create Offer",
        description="Create a new offer. Only authenticated users can create offers.",
        request=OfferCreateSerializer,
        responses={201: OfferListSerializer},
        examples=[OFFERS_EMPTY_RESPONSE, OFFERS_LIST_RESPONSE],
        tags=["Offers"]
    )
)


offer_detail_doc = extend_schema_view(
    get=extend_schema(
        summary='Retrieve Offer Details',
        description='Retrieve full details of a single offer by UUID. Sender or assigned carrier must be authenticated. Includes all steps data, pricing, receiver details, and media.',
        responses={200: OfferSerializer, 404: OpenApiTypes.OBJECT},
        examples=[OFFERS_LIST_RESPONSE, OFFERS_EMPTY_RESPONSE],
        tags=['Offers'],
    )
)

offer_step_details_doc = extend_schema_view(
    patch=extend_schema(
        summary='Update Offer Details Step',
        description='Update the details step of an offer. Sender must be the owner. Required fields: package_type, is_fragile, description. Returns updated `current_step`.',
        request=OfferDetailsSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[OFFER_STEP_ERROR_RESPONSE],
        tags=['Offers'],
    )
)

offer_pricing_doc = extend_schema_view(
    patch=extend_schema(
        summary='Update Offer Pricing Step',
        description='Update the pricing step of an offer. Required fields: base_price, is_urgent. Total price will be calculated automatically.',
        request=OfferPricingSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[OFFER_STEP_ERROR_RESPONSE],
        tags=['Offers'],
    )
)


offer_location_doc = extend_schema_view(
    patch=extend_schema(
        summary='Update Offer Location Step',
        description='Update the location step of an offer. Required fields: pickup_location, delivery_location, pickup_time. Sender must be the owner.',
        request=OfferLocationSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[OFFER_STEP_ERROR_RESPONSE],
        tags=['Offers'],
    )
)


offer_review_doc = extend_schema_view(
    get=extend_schema(
        summary='Review Offer Before Posting',
        description=(
            "Retrieve a complete summary of the offer before posting. "
            "This endpoint aggregates all steps (details, location, pricing, receiver info). "
            "Used by frontend to show confirmation screen before publishing."
        ),
        responses={
            200: OfferListSerializer,
            404: OpenApiTypes.OBJECT
        },
        examples=[OFFER_REVIEW_RESPONSE],
        tags=['Offers'],
    ),
    patch=extend_schema(
        summary='Patch data to update Offer Before Posting',
        description=(
            "Update the offer before posting. "
            "This endpoint aggregates all steps (details, location, pricing, receiver info). "
            "Used by frontend to upload all offer details at a go."
        ),
        request=OfferUpdateSerializer,
        responses={
            200: OfferUpdateSerializer,
            404: OpenApiTypes.OBJECT
        },
        examples=[OFFER_REVIEW_RESPONSE, OFFER_UPDATE_RESPONSE],
        tags=['Offers'],
    )
)

offer_transition_doc = extend_schema_view(
    post=extend_schema(
        summary='Transition Offer State',
        description=(
            "Change the state of an offer using an action. "
            "This enforces the offer lifecycle (draft → posted → accepted → in_transit → delivered). "
            "Validation ensures only allowed transitions occur. First time an order is posted, carriers in 10kn radius receives a notification."
        ),
        request=OfferTransitionSerializer,
        responses={
            200: OfferTransitionSerializer,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT
        },
        examples=[
            OFFER_TRANSITION_REQUEST,
            OFFER_TRANSITION_SUCCESS,
            OFFER_TRANSITION_ERROR
        ],
        tags=['Offers'],
    )
)

proposal_doc = extend_schema_view(
    list=extend_schema(
        summary='List Proposals',
        description='Retrieve proposals for the logged-in user: Senders see proposals for their offers, carriers see their own proposals.',
        responses={200: ProposalSerializer},
        tags=['Proposals'],
    ),
    create=extend_schema(
        summary='Create Proposal',
        description='Carrier submits a proposal for a posted offer.',
        request=ProposalSerializer,
        responses={201: ProposalSerializer, 400: PROPOSAL_CREATE_FAILED_RESPONSE},
        examples=[PROPOSAL_CREATE_REQUEST, PROPOSAL_CREATE_FAILED_RESPONSE],
        tags=['Proposals'],
    ),
    accept=extend_schema(
        summary='Accept Proposal',
        description='Sender accepts a carrier\'s proposal. The proposal and offer statuses are updated and an escrow is created.',
        responses={200: PROPOSAL_ACCEPT_RESPONSE, 400: PROPOSAL_CREATE_FAILED_RESPONSE},
        examples=[PROPOSAL_ACCEPT_RESPONSE],
        methods=['POST'],
        tags=['Proposals'],
    ),
    reject=extend_schema(
        summary='Reject Proposal',
        description='Sender rejects a carrier\'s proposal.',
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[PROPOSAL_REJECT_RESPONSE],
        methods=['POST'],
        tags=['Proposals'],
    ),
)