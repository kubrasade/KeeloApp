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

            message_data = await self.get_message_data(message_obj)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_data": message_data
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message_data": event["message_data"]
        }))

    @database_sync_to_async
    def get_first_user(self):
        return User.objects.first()

    @database_sync_to_async
    def save_message(self, sender, content):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(chat_room=room, sender=sender, content=content)

    @database_sync_to_async
    def get_message_data(self, message):
        return {
            "id": message.id,
            "sender": {
                "id": message.sender.id,
                "first_name": message.sender.first_name,
                "last_name": message.sender.last_name
            },
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "image": message.image.url if message.image else None,
            "file": message.file.url if message.file else None
        }

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