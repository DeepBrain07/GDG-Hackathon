from django.urls import path
from .views import InterswitchWebhookView, WebFundingPayloadView,WebFundingUploadPayloadView

urlpatterns = [
    path("fund/webhook/interswitch/", InterswitchWebhookView.as_view(), name="interswitch-webhook"),
    path("fund/web/create_payload/", WebFundingPayloadView.as_view(), name="create_web_funding_payload"),
    path("fund/web/upload_payload/", WebFundingUploadPayloadView.as_view(), name="upload_web_funding_payload"),
]
