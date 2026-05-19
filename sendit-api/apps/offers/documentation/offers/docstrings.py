from drf_spectacular.utils import OpenApiExample, extend_schema
from drf_spectacular.types import OpenApiTypes

# Empty list response
OFFERS_EMPTY_RESPONSE = OpenApiExample(
    'No offers',
    summary='No offers found matching filters',
    value={"count": 0, "message": "No offers match found", "offers": []},
    response_only=True,
    status_codes=['200']
)

# List of offers response
OFFERS_LIST_RESPONSE = OpenApiExample(
    'Offers list',
    summary='List of offers',
    value={
        "count": 2,
        "offers": [
            {
                "id": "uuid-1",
                "code": "ABC123",
                "status": "posted",
                "current_step": "details",
                "pickup_location": {"id": "loc1", "name": "Warehouse A"},
                "delivery_location": {"id": "loc2", "name": "Customer B"},
                "base_price": "1000.00",
                "total_price": "1100.00",
                "is_urgent": False
            },
            {
                "id": "uuid-2",
                "code": "XYZ456",
                "status": "posted",
                "current_step": "location",
                "pickup_location": {"id": "loc3", "name": "Warehouse C"},
                "delivery_location": {"id": "loc4", "name": "Customer D"},
                "base_price": "2000.00",
                "total_price": "2200.00",
                "is_urgent": True
            }
        ]
    },
    response_only=True,
    status_codes=['200']
)

# Offer step update error example
OFFER_STEP_ERROR_RESPONSE = OpenApiExample(
    'Step Validation Error',
    summary='Invalid step data',
    value={"error": True, "message": "Package type is required"},
    response_only=True,
    status_codes=['400']
)

OFFER_REVIEW_RESPONSE = OpenApiExample(
    'Offer Review',
    summary='Full offer review before posting',
    value={
        "success": True,
        "data": {
            "id": "uuid-123",
            "code": "ABC123",
            "package_type": "small",
            "is_fragile": False,
            "description": "Handle with care",
            "media": [
                {"id": "media1", "url": "https://..."}
            ],
            "pickup_location": {
                "name": "Warehouse A",
                "address": "Ikeja, Lagos"
            },
            "delivery_location": {
                "name": "Customer B",
                "address": "Lekki, Lagos"
            },
            "pickup_time": "2026-03-22T10:00:00Z",
            "base_price": "1000.00",
            "is_urgent": True,
            "urgent_fee": "1000.00",
            "platform_fee": "100.00",
            "total_price": "2000.00",
            "receiver_name": "John Doe",
            "receiver_phone": "+2348000000000"
        }
    },
    response_only=True,
    status_codes=['200']
)
OFFER_UPDATE_RESPONSE = OpenApiExample(
    'Offer Update',
    summary='Full offer update before posting',
    value={
        "success": True,
        "data":{ "package_type": "large", "is_fragile": "false", "pickup_location": { "city": "Ogbomosho", "area": "Under-G", "street": "LAUTECH Main Road", "landmark": "LAUTECH Second Gate", "latitude": 8.1229, "longitude": 4.2480 }, "delivery_location": { "city": "Ibadan", "area": "Iwo Road", "street": "Iwo Road Interchange", "landmark": "Iwo Road Roundabout / Motor Park", "latitude": 7.3971, "longitude": 3.9402 }, "is_urgent": "false", "base_price": 5000.0, "receiver_name": "Akinwale Bobo", "receiver_phone": "08033145678" }
    },
    response_only=True,
    status_codes=['200']
)


OFFER_TRANSITION_REQUEST = OpenApiExample(
    'Post Offer',
    summary='Move offer from draft to posted',
    value={
        "action": "post"
    },
    request_only=True,
)

OFFER_TRANSITION_SUCCESS = OpenApiExample(
    'Transition Success',
    summary='Offer successfully transitioned',
    value={
        "success": True,
        "message": "OFFER STATUS UPDATE SUCCESS",
        "data": {
            "id": "uuid-123",
            "status": "posted",
            "current_step": "posted"
        }
    },
    response_only=True,
    status_codes=['200']
)

OFFER_TRANSITION_ERROR = OpenApiExample(
    'Invalid Transition',
    summary='Invalid state transition',
    value={
    "error": True,
    "message": "You cannot post an incomplete offer"
    },
    response_only=True,
    status_codes=['400']
)


PROPOSAL_CREATE_REQUEST = OpenApiExample(
    'Create Proposal',
    summary='Carrier submits a proposal for an offer',
    value={
        "offer": 10
    },
    request_only=True,
)

PROPOSAL_CREATE_FAILED_RESPONSE = OpenApiExample(
    'Create Proposal Failed Response',
    summary='Response when a sender creates a proposal failed',
    value={
        "message": "Proposal created failed with error message either offer not found or offer is not posted"
    },
    response_only=True,
)

PROPOSAL_ACCEPT_RESPONSE = OpenApiExample(
    'Accept Proposal Response',
    summary='Response when a sender accepts a proposal',
    value={
        "message": "Proposal accepted successfully",
        "data": {
            "proposal_id": 1,
            "escrow_id": 100,
            "amount": 1000
        }
    },
    response_only=True,
)

PROPOSAL_REJECT_RESPONSE = OpenApiExample(
    'Reject Proposal Response',
    summary='Response when a sender rejects a proposal',
    value={
        "message": "Proposal rejected successfully"
    },
    response_only=True,
)
