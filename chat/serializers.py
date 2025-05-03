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


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ChatRoomSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    dietitian = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'client', 'dietitian', 'created_at', 'last_message', 'unread_count']
        read_only_fields = ['id', 'created_at']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'content': last_message.content,
                'created_at': last_message.created_at,
                'sender_id': last_message.sender.id
            }
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return MessageRead.objects.filter(
            message__chat_room=obj,
        ).exclude(user=user).count()


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(write_only=True)
    dietitian_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'client_id', 'dietitian_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if data['client_id'] == data['dietitian_id']:
            raise serializers.ValidationError("Client and dietitian cannot be the same user.")
        return data

    def create(self, validated_data):
        client = User.objects.get(id=validated_data.pop('client_id'))
        dietitian = User.objects.get(id=validated_data.pop('dietitian_id'))
        return ChatRoom.objects.create(client=client, dietitian=dietitian)