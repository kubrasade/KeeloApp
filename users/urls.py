from django.urls import path
from .views import (
    UserListCreateView, UserRetrieveUpdateDestroyView, me,
    DietitianProfileListCreateView, DietitianProfileRetrieveUpdateDestroyView,
    ClientProfileListCreateView, ClientProfileRetrieveUpdateDestroyView,
    SpecializationListCreateView, SpecializationRetrieveUpdateDestroyView,
    HealthMetricListCreateView, HealthMetricRetrieveUpdateDestroyView
)

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-retrieve-update-destroy'),
    path('users/me/', me, name='user-me'),

    path('dietitians/', DietitianProfileListCreateView.as_view(), name='dietitian-list-create'),
    path('dietitians/<int:pk>/', DietitianProfileRetrieveUpdateDestroyView.as_view(), name='dietitian-retrieve-update-destroy'),

    path('clients/', ClientProfileListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientProfileRetrieveUpdateDestroyView.as_view(), name='client-retrieve-update-destroy'),

    path('specializations/', SpecializationListCreateView.as_view(), name='specialization-list-create'),
    path('specializations/<int:pk>/', SpecializationRetrieveUpdateDestroyView.as_view(), name='specialization-retrieve-update-destroy'),

    path('health-metrics/', HealthMetricListCreateView.as_view(), name='health-metric-list-create'),
    path('health-metrics/<int:pk>/', HealthMetricRetrieveUpdateDestroyView.as_view(), name='health-metric-retrieve-update-destroy'),
] 