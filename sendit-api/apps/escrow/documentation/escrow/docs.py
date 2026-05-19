from drf_spectacular.utils import  OpenApiExample


ESCROW_FUND_RESPONSE = OpenApiExample(
    'Escrow Funded',
    summary='Escrow funded successfully',
    value={
        "message": "Escrow funded successfully",
        "data": {
            "id": 5,
            "amount": 5000.0,
            "status": "FUNDED"
        }
    },
    response_only=True,
)

ESCROW_RELEASE_REQUEST = OpenApiExample(
    'Release Escrow',
    summary='Release full escrow amount to carrier',
    description='Optional: provide amount for partial release (defaults to full escrow amount)',
    value={
        "amount": 3000.0
    },
    request_only=True,
)

ESCROW_RELEASE_RESPONSE = OpenApiExample(
    'Escrow Released',
    summary='Funds released to carrier wallet',
    value={
        "status": "Funds released"
    },
    response_only=True,
)

ESCROW_DISPUTE_REQUEST = OpenApiExample(
    'Dispute Escrow',
    summary='Admin resolves dispute by splitting escrow funds',
    description=(
        "⚠️ REQUIRED FIELDS:\n"
        "- release_amount_to_carrier: float\n"
        "- note: string\n\n"
        "Business Logic:\n"
        "- release_amount_to_carrier → paid to carrier\n"
        "- (escrow.amount - release_amount_to_carrier) → refunded to sender\n"
        "- Must not exceed total escrow amount"
    ),
    value={
        "release_amount_to_carrier": 2000.0,
        "note": "Carrier delayed delivery, partial refund issued to sender"
    },
    request_only=True,
)

ESCROW_DISPUTE_RESPONSE = OpenApiExample(
    'Dispute Resolved',
    summary='Escrow dispute handled and funds split',
    value={
        "note": "the carrier didn't deliver it well "
    },
    response_only=True,
)