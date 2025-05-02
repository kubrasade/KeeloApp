from django.db import models
from django.conf import settings
from core.models import BaseModel


class ChatRoom(BaseModel):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_chat_rooms'
    )
    dietitian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dietitian_chat_rooms'
    )

    class Meta:
        unique_together = ('client', 'dietitian')
        ordering = ['-updated_at']

    def __str__(self):
        return f'Chat between {self.client.get_full_name()} and {self.dietitian.get_full_name()}'