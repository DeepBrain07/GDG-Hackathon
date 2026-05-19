from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiTypes

# Examples
WALLET_404_RESPONSE = OpenApiExample(
    '404 NOT FOUND',
    summary='Wallet not found for user.',
    value={"detail": "Wallet not found."},
    response_only=True,
    status_codes=['404']
)

WALLET_HISTORY_RESPONSE = OpenApiExample(
    'Wallet History Example',
    summary='Paginated ledger and transaction history',
    value={
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 1,
                "type": "ledger",
                "sub_type": "credit",
                "amount": "5000.00",
                "note": "Top-up",
                "status": "completed",
                "created_at": "2026-03-25T10:00:00Z"
            },
            {
                "id": 2,
                "type": "transaction",
                "sub_type": "funding",
                "amount": "5000.00",
                "note": "Wallet top-up via Interswitch",
                "status": "success",
                "created_at": "2026-03-25T10:05:00Z"
            }
        ]
    },
    response_only=True,
    status_codes=['200']
)

