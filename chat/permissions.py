from rest_framework import permissions
from .models import ChatRoom, Message


class IsChatRoomParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: ChatRoom):
        return obj.client == request.user or obj.dietitian == request.user

    def has_permission(self, request, view):
        return True


class IsMessageSender(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Message):
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.chat_room.client == request.user or
                obj.chat_room.dietitian == request.user
            )
        return obj.sender == request.user