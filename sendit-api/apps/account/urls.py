from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import token_views, phone_views
from .views.social_auth import GoogleLogin, GoogleAuthConfig
from .views.verification_view import VerificationViewSet

router = DefaultRouter()
router.register(r"verifications", VerificationViewSet, basename="verification") 

# showing token in the response
urlpatterns = [
    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('google/config/', GoogleAuthConfig.as_view(), name='google_config'),
    path('me/', view=token_views.MeView.as_view(), name='user_details'),
    path('signout/', view=token_views.LogoutView.as_view(), name='logout_user'),
    path('<uuid:user_id>/profiles/',token_views.ProfileView.as_view(),name='user_profiles'),
    path('login/', view=token_views.LoginView.as_view(), name='login_user'),

    # phone verification
    path('phone/request-otp/', phone_views.RequestPhoneOTPView.as_view(), name='request_phone_otp'),
    path('phone/verify-otp/', phone_views.VerifyPhoneOTPView.as_view(), name='verify_phone_otp'),
    
#     path('signup/', view=token_views.RegisterView.as_view(), name='register_user'),
#     path('signup/verify-email-otp/',
#          view=token_views.EmailVerifyOTPView.as_view(), name='verify_email_otp'),
#     path('signup/email-resend-otp/',
#          view=token_views.EmailResendOTPView.as_view(), name='email_resend_otp'),
#     path('refresh/', view=token_views.TokenRefreshView.as_view(), name='token_refresh'),

#     # forgotten password
#     path('password-reset/', view=token_views.PasswordResetRequestOTPView.as_view(),
#          name='password_reset'),
#     path('password-reset/verify-password-otp/',view=token_views.PasswordResetVerifyView.as_view(), name='verify_password_otp'),

    path("",include(router.urls)),
]
