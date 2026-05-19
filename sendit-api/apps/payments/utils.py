import hmac, hashlib

def verify_signature(request_body, signature, secret):

    computed = hmac.new(
        secret.encode(),
        request_body,
        hashlib.sha512
    ).hexdigest()

    return computed == signature

