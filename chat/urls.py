from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.ChatRoomListCreateView.as_view(), name='chat-room-list-create'),
    path('rooms/<int:pk>/', views.ChatRoomRetrieveView.as_view(), name='chat-room-retrieve'),

    path('rooms/<int:chat_room_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', views.MessageRetrieveUpdateDestroyView.as_view(), name='message-retrieve-update-destroy'),

    path('messages/<int:message_id>/read/', views.MessageReadView.as_view(), name='message-read'),
    
    path('rooms/<int:chat_room_id>/unread-count/', views.UnreadMessageCountView.as_view(), name='unread-message-count'),
    
    path('rooms/<int:chat_room_id>/mark-messages-as-read/', views.MarkMessagesAsReadView.as_view(), name='mark-messages-as-read'),
]