import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from apps.core.models import Message, ChatRoom
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        
        # --- TESTING BYPASS ---
        # If testing with Postman and no JWT middleware yet, scope['user'] is Anonymous.
        # We manually check or assign a fallback for testing purposes.
        user = self.scope.get("user", AnonymousUser())

        if not message_text:
            return

        # If user is anonymous, database save will fail due to null sender.
        # Only attempt save if we have a real user.
        if not user.is_anonymous:
            saved_msg = await self.save_message(user, message_text)
            response_data = {
                'type': 'chat_message',
                'message': saved_msg.text,
                'sender_id': str(user.id),
                'sender_name': user.get_full_name() or user.username,
                'timestamp': saved_msg.timestamp.isoformat()
            }
        else:
            # Fallback response for Postman testing when unauthenticated
            response_data = {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': "0",
                'sender_name': "Postman Test User",
                'timestamp': timezone.now().isoformat()
            }

        await self.channel_layer.group_send(self.room_group_name, response_data)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, sender, text):
        return Message.objects.create(
            room_id=self.room_id, 
            sender=sender, 
            text=text
        )

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user", AnonymousUser())
        
        if self.user.is_anonymous:
            self.group_name = "notify_test_group"
        else:
            # Ensure this is a string to match the UUID in the logs
            self.group_name = f"notify_{str(self.user.id)}"
            
        print(f"WS CONNECT: User {self.user} joined {self.group_name}", flush=True)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    # ... disconnect logic ...

    async def send_notification(self, event):
        # 1. Get the data out of the 'content' key sent by the service
        notification_data = event.get("content", {})
        
        print(f"WS DATA RECEIVED IN CONSUMER: {notification_data}", flush=True)

        # 2. Send it to the frontend
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': notification_data.get('title'),
            'message': notification_data.get('message'),
            'created_at': notification_data.get('created_at'),
            'id': notification_data.get('id'),
        }))