from django.urls import path
from .views import (
    NotificationListView,
    NotificationRetrieveUpdateView,
    NotificationMarkAllAsReadView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', NotificationRetrieveUpdateView.as_view(), name='notification-retrieve-update'),
    path('mark-all-as-read/', NotificationMarkAllAsReadView.as_view(), name='notification-mark-all-as-read'),
] 