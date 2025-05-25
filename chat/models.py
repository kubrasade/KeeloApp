from django.db import models
from django.conf import settings
from core.models import BaseModel
from users.models import ClientProfile, DietitianProfile


class ChatRoom(BaseModel):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name='client_chat_rooms'
    )
    dietitian = models.ForeignKey(
        DietitianProfile,
        on_delete=models.CASCADE,
        related_name='dietitian_chat_rooms'
    )

    class Meta:
        unique_together = ('client', 'dietitian')
        ordering = ['-updated_at']

    def __str__(self):
        return f'Chat between {self.client.get_full_name()} and {self.dietitian.get_full_name()}'
    

class Message(BaseModel):
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField(blank=True, null= True)
    image = models.ImageField(blank=True, null= True)
    file = models.FileField(blank=True, null= True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.get_full_name()} at {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class MessageRead(BaseModel):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_by'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='read_messages'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')

    def __str__(self):
        return f'Message {self.message.id} read by {self.user.get_full_name()}'
