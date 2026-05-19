from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Location, Notification, Media, Message, ChatRoom

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'avatar']

    def get_avatar(self, obj):
        try:
            profile = getattr(obj, 'profile', None)
            if profile:
                avatar_media = profile.avatar 
                if avatar_media:
                    return avatar_media.file_url
        except Exception:
            pass
        return None

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file_url', 'tag', 'order', 'uploaded_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.first_name')
    sender_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_name', 'sender_avatar', 'text', 'timestamp']

    def get_sender_avatar(self, obj):
        if not obj.sender:
            return None
        # Reuse the logic from UserSerializer
        try:
            profile = getattr(obj.sender, 'profile', None)
            if profile and profile.avatar:
                return profile.avatar.file_url
        except Exception:
            pass
        return None

class ChatRoomSerializer(serializers.ModelSerializer):
    # Set to read_only=True so the POST /chats/ doesn't require a participants list
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 
            'participants', 
            'last_message', 
            'unread_count', 
            'updated_at', 
            'offer_id'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return {
                'text': last_msg.text,
                'sender_id': last_msg.sender.id if last_msg.sender else None,
                'sender_name': last_msg.sender.first_name if last_msg.sender else "System",
                'timestamp': last_msg.timestamp
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Counts messages not read by the current user, excluding their own messages
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'area', 'street', 'landmark', 'latitude', 'longitude']

class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', "title", 'is_read', "object_id",'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'is_read', 'created_at', 'title', 'message', "object_id"]