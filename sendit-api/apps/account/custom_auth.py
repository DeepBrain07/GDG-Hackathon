from drf_spectacular.extensions import OpenApiAuthenticationExtension
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck, get_authorization_header

SAFE_METHODS = ('GET', "HEAD", "OPTIONS")


class CookieJWTAuthentication(JWTAuthentication):

    def enforce_csrf(self, request):
        """Enforce CSRF validation for unsafe methods"""
        def dummy_get_response(request):
            return None
        check = CSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise AuthenticationFailed('CSRF Failed: %s' % reason)

    def authenticate(self, request):
        print("!!! COOKIE AUTH CLASS IS RUNNING !!!")
        
        # DEBUG: See everything the browser sent
        print(f"All Cookies Found: {request.COOKIES.keys()}")
        
        # Attempt to get the specific cookie name from settings
        cookie_name = settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token')
        raw_token = request.COOKIES.get(cookie_name)
        
        print(f"Target Cookie Name: {cookie_name}")
        print(f"Token Value Found: {'[EXISTS]' if raw_token else '[NONE]'}")

        if raw_token:
            try:
                validated = self.get_validated_token(raw_token)
                if request.method not in SAFE_METHODS:
                    self.enforce_csrf(request)
                return self.get_user(validated), validated
            except Exception as e:
                print(f"❌ TOKEN VALIDATION FAILED: {str(e)}")
                pass 

        # 2. Check Header Fallback (Axios interceptor should hit this if cookie fails)
        auth = get_authorization_header(request).split()
        if auth and len(auth) == 2:
            try:
                validated = self.get_validated_token(auth[1].decode())
                print("✅ Authenticated via Header")
                return self.get_user(validated), validated
            except Exception as e:
                print(f"❌ HEADER AUTH FAILED: {e}")
        
        return None
class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'apps.account.custom_auth.CookieJWTAuthentication'
    name = 'cookieJWTAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access_token'
        }