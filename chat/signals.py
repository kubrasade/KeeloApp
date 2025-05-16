from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import MessageSerializer

@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f'chat_{instance.chat_room.id}'
        message_data = MessageSerializer(instance).data
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat_message',
                'message_data': message_data
            }
        )