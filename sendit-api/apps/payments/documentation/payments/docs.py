from drf_spectacular.utils import OpenApiExample



WEB_FUNDING_400_RESPONSE = OpenApiExample(
    '400 BAD REQUEST',
    summary='Missing or invalid amount',
    description='Returned when the `amount` field is missing or invalid.',
    value={'error': "Amount is required"},
    response_only=True,
    status_codes=['400']
)

WEB_FUNDING_200_RESPONSE = OpenApiExample(
    '200 OK',
    summary='Funding initiated successfully',
    description='Returned when a wallet funding transaction is successfully created and payload is generated.',
    value={
        "message": "Funding initiated",
        "transaction_id": 123,
        "form_payload": {
            "merchantId": "XYZ123",
            "transactionRef": "TXN_123ABC",
            "amount": 5000,
            "currency": "NGN",
            "redirectUrl": "https://yourapp.com/payment/callback",
            # ... other payload fields
        }
    },
    response_only=True,
    status_codes=['200']
)

WEB_FUNDING_REQUEST = OpenApiExample(
    'FUNDING REQUEST',
    summary='Payload of succesfully funding from interswitch',
    description='Returned when a wallet funding transaction is successfully. both `amount` and `txn_ref` are required',
    value= {
            "amount": 50000, 
            "cardNumber": "5399********1234",
            "txnRef": "844528362159",
            "paymentReference": "UBA|API|MX210|27-03-2026|310245|821743",
            "retrievalReferenceNumber": "000782194352",
            "splitAccounts": [],
            "transactionDate": "2026-03-27T09:30:15",
            "resp": "00",
            "responseDescription": "Approved by Financial Institution",
            "accountNumber": "9999999999"
            # ... other payload fields
            },

 
    response_only=True,
    status_codes=['200']
)
