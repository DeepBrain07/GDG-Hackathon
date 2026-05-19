from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()

# 1. Notifications Endpoint
router.register(r'notifications', views.NotificationListView, basename='notification')

# 2. Chats Endpoint (The one we just created)
router.register(r'chats', views.ChatRoomViewSet, basename='chat')

# 3. Media Endpoint (For uploading/deleting files)
router.register(r'media', views.MediaViewSet, basename='media')


urlpatterns = [
    path("", include(router.urls)),
]