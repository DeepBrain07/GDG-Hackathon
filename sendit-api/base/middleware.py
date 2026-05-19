import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # 1. Get the token from the query string (e.g., ?token=...)
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")

        if token:
            try:
                # 2. Decode the JWT (assuming SimpleJWT's default settings)
                decoded_data = jwt.decode(
                    token[0], 
                    settings.SECRET_KEY, 
                    algorithms=["HS256"]
                )
                user_id = decoded_data.get("user_id")
                # 3. Attach the user to the scope
                scope["user"] = await get_user(user_id)
            except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)