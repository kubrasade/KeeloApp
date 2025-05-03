import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, MessageRead

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        
        setattr(self, "room_group_name", self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        user = self.scope.get("user")
        if not user or user.is_anonymous:
            self.scope["user"] = await self.get_first_user()

    async def disconnect(self, close_code):
        room_group_name = getattr(self, "room_group_name", None)
        if room_group_name:
            await self.channel_layer.group_discard(room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope.get("user")

        if data.get("type") == "chat_message":
            message = data["message"]
            message_obj = await self.save_message(user, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": user.id,
                    "message_id": message_obj.id,
                    "timestamp": message_obj.created_at.isoformat()
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "sender_id": event["sender_id"],
            "message_id": event["message_id"],
            "timestamp": event["timestamp"]
        }))

    @database_sync_to_async
    def get_first_user(self):
        return User.objects.first()

    @database_sync_to_async
    def save_message(self, sender, content):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(chat_room=room, sender=sender, content=content)

    @database_sync_to_async
    def mark_message_as_read(self, message, user):
        MessageRead.objects.get_or_create(message=message, user=user)

    @database_sync_to_async
    def mark_message_as_read_by_id(self, message_id, user):
        message = Message.objects.get(id=message_id)
        MessageRead.objects.get_or_create(message=message, user=user)

    @database_sync_to_async
    def update_user_status(self, is_online):
        user = self.scope.get("user")
        if user and not user.is_anonymous:
            user.is_online = is_online
            user.save()