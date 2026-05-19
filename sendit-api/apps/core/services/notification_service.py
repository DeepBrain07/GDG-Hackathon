from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.core.models import Notification
from apps.core.serializers import NotificationSerializer # Assuming you have this

class NotificationService:

    @staticmethod
    def _push_to_websocket(user_id, notification):
        user_id_str = str(user_id) # Force string
        print(f"DEBUG: Attempting WebSocket push to group notify_{user_id_str}")
        
        channel_layer = get_channel_layer()
        
        # Manually extract primitive data to avoid Serializer/UUID/DateTime issues
        payload = {
            "id": str(notification.id),
            "title": str(notification.title),
            "message": str(notification.message),
            "type": str(notification.type),
            "created_at": notification.created_at.isoformat() if notification.created_at else None
        }
        
        async_to_sync(channel_layer.group_send)(
            f"notify_{user_id_str}",
            {
                "type": "send_notification",
                "content": payload  # This is now 100% safe for Redis
            }
        )
        
    @staticmethod
    def create(user, type, title, message, content_object=None):
        # 1. Save to DB
        notification = Notification.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            content_object=content_object
        )

        # 2. Push Real-time
        try:
            NotificationService._push_to_websocket(user.id, notification)
        except Exception as e:
            # We wrap this so a socket error doesn't crash the whole DB transaction
            print(f"WebSocket Push Error: {e}")

        return notification

    @staticmethod
    def bulk_create(data_list):
        # Ensure created_at isn't in the data if it's auto-generated
        for data in data_list:
            data.pop('created_at', None) 
            
        notifications = [Notification(**data) for data in data_list]
        
        # Save to DB
        created_objs = Notification.objects.bulk_create(notifications)
        
        # Push to WebSocket (optional, but keep for real-time)
        for obj in created_objs:
            try:
                NotificationService._push_to_websocket(obj.user.id, obj)
            except Exception:
                pass
                
        return created_objs