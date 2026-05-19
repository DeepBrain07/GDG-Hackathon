from django.urls import path
from .views import WaitlistCreateView, SubscribeCreateView

urlpatterns = [
    path('waitlist/', WaitlistCreateView.as_view(), name='api-waitlist'),
    path('subscribe/', SubscribeCreateView.as_view(), name='api-subscribe'),
]