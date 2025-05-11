from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatRoom, Message, MessageRead
from .serializers import (
    ChatRoomSerializer, 
    MessageSerializer,
    MessageReadSerializer,ChatRoomCreateSerializer
)
from .permissions import IsClientOrDietitian
from .permissions import IsChatRoomParticipant, IsMessageSender
from rest_framework.parsers import MultiPartParser, FormParser


class ChatRoomListCreateView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def perform_create(self, serializer):
        serializer.save()
            
class ChatRoomRetrieveView(generics.RetrieveAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, IsChatRoomParticipant]

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsChatRoomParticipant]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        return Message.objects.filter(chat_room_id=chat_room_id)

    def perform_create(self, serializer):
        chat_room = ChatRoom.objects.get(id=self.kwargs['chat_room_id'])
        serializer.save(chat_room=chat_room, sender=self.request.user)

class MessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, IsMessageSender]

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return MessageReadSerializer
        return MessageSerializer

    def perform_update(self, serializer):
        if 'is_read' in serializer.validated_data:
            serializer.save()
        else:
            serializer.save(sender=self.request.user)

class MessageReadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsClientOrDietitian]
    serializer_class = MessageReadSerializer

    def create(self, request, *args, **kwargs):
        message_id = self.kwargs.get('message_id')
        message = Message.objects.get(id=message_id)
        
        chat_room = message.chat_room
        if not (chat_room.client.user == request.user or chat_room.dietitian.user == request.user):
            return Response(
                {"detail": "You are not part of this chat room."},
                status=status.HTTP_403_FORBIDDEN
            )

        MessageRead.objects.get_or_create(
            message=message,
            user=request.user
        )

        return Response(
            {"detail": "Message marked as read."},
            status=status.HTTP_201_CREATED
        )

class UnreadMessageCountView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        chat_room_id = self.kwargs['chat_room_id']
        unread_count = Message.objects.filter(
            chat_room_id=chat_room_id
        ).exclude(
            message_read__user=request.user
        ).count()
        
        return Response({'unread_count': unread_count})

class MarkMessagesAsReadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        chat_room_id = self.kwargs['chat_room_id']
        message_ids = request.data.get('message_ids', [])
        
        messages = Message.objects.filter(
            id__in=message_ids,
            chat_room_id=chat_room_id
        )
        
        for message in messages:
            MessageRead.objects.get_or_create(
                user=request.user,
                message=message
            )
        
        return Response(status=status.HTTP_200_OK) 
