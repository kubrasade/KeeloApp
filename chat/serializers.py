from rest_framework import serializers
from .models import ChatRoom, Message, MessageRead
from django.contrib.auth import get_user_model
from users.models import ClientProfile, DietitianProfile 
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ['id', 'username', 'first_name', 'last_name']

class SimpleClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = ('id', 'user')

class SimpleDietitianProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DietitianProfile
        fields = ('id', 'user',)

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
        fields = ['id', 'chat_room', 'sender', 'content', 'created_at', 'file', 'image']
        read_only_fields = ['id', 'created_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    client = SimpleClientProfileSerializer(read_only=True)
    dietitian = SimpleDietitianProfileSerializer(read_only=True)
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
        unread_count = Message.objects.filter(
            chat_room=obj
        ).exclude(
            read_by__user=user
        ).count()  
        return unread_count
    
class ChatRoomCreateSerializer(serializers.ModelSerializer):
    dietitian_id = serializers.IntegerField(write_only=True)
    client_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'dietitian_id', 'client_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        dietitian_id = data.get('dietitian_id')
        client_id = data.get('client_id')

        if not client_id:
            raise serializers.ValidationError("Client profile is required.")
        if not ClientProfile.objects.filter(id=client_id).exists():
            raise serializers.ValidationError("Client profile does not exist.")
        client_profile = ClientProfile.objects.get(id=client_id)

        if not dietitian_id:
            raise serializers.ValidationError("Dietitian is required.")
        if not DietitianProfile.objects.filter(id=dietitian_id).exists():
            raise serializers.ValidationError("Dietitian profile does not exist.")
        dietitian_profile = DietitianProfile.objects.get(id=dietitian_id)

        if client_profile.user.id == dietitian_profile.user.id:
            raise serializers.ValidationError("Client and dietitian cannot be the same user.")
        
        return data

    def create(self, validated_data):
        client_id = validated_data.pop('client_id')
        dietitian_id = validated_data.pop('dietitian_id')
        client_profile = ClientProfile.objects.get(id=client_id)
        dietitian_profile = DietitianProfile.objects.get(id=dietitian_id)

        existing = ChatRoom.objects.filter(client=client_profile, dietitian=dietitian_profile).first()
        if existing:
            return existing

        chat_room = ChatRoom.objects.create(client=client_profile, dietitian=dietitian_profile)
        return chat_room