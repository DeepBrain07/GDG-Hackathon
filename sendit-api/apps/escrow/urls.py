
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EscrowViewSet

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'', EscrowViewSet, basename='escrow')

urlpatterns = [
    path('', include(router.urls)),
]
