from rest_framework import serializers
from .models import ChatRoom, Message, MessageRead
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class MessageReadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MessageRead
        fields = ['id', 'user', 'read_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


