import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from apps.account.serializers import UserSerializer, GoogleLoginSerializer
from apps.account.documentation.account.schemas import google_login_doc, google_auth_config_doc
from apps.account.utils import send_login_or_logout_email, set_auth_cookies
from apps.wallets.services.wallet_services import WalletService
User = get_user_model()

@google_login_doc
class GoogleLogin(APIView):
    serializer_class = GoogleLoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        """
        Google Login View
        Supports both ID Token (JWT) and Access Token (OAuth2).
        """
        token_str = request.data.get("id_token") or request.data.get("access_token")
        
        if not token_str:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        idinfo = None
        # 1. Attempt to verify as ID Token (JWT) - Common for standard Google Buttons
        try:
            idinfo = id_token.verify_oauth2_token(
                token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            # 2. Fallback: Verify as Access Token - Common for useGoogleLogin React Hook
            user_info_res = requests.get(
                f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={token_str}'
            )
            if user_info_res.status_code == 200:
                idinfo = user_info_res.json()
            else:
                return Response(
                    {"error": "Invalid Google token or expired"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        email = idinfo.get("email")
        name = idinfo.get("name")

        if not email:
            return Response({"error": "Email not found in Google profile"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": name.split(" ")[0] if name else "",
                "last_name": " ".join(name.split(" ")[1:]) if name else "",
            }
        )

        if created:
            user.set_unusable_password()
            user.is_active = True
            user.save()

            # Handle profile creation if method exists
            if hasattr(user, 'create_profile'):
                user.create_profile()
            WalletService.create_wallet_account(user)

        # Trigger login notification email
        send_login_or_logout_email(user, request, 'login')

        # 4. Generate Tokens (Assumes your User model has a get_jwt_tokens property/method)
        tokens = user.get_jwt_tokens 

        data = {
            'status': 'Success',
            'message': 'Authenticated successfully!',
            'data': UserSerializer(user).data,
            'token': tokens
        }
        response = Response(data=data, status=status.HTTP_201_CREATED)

        # Use the utility instead of manual set_cookie
        return set_auth_cookies(response, tokens)

@google_auth_config_doc
class GoogleAuthConfig(APIView):
    """
    Returns the Google Client ID for the frontend to initialize the OAuth provider.
    """
    def get(self, request):
        return Response({
            'client_id': settings.GOOGLE_CLIENT_ID,
        }, status=status.HTTP_200_OK)
