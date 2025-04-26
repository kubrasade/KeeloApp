from django.urls import path
from .views import (
    SpecializationChoiceListCreateView,
    DietitianListBySpecializationView,
    MatchingListCreateView,
    MatchingRetrieveUpdateDestroyView,
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
    ReviewStatusView
)

urlpatterns = [
    path('specialization-choices/', SpecializationChoiceListCreateView.as_view(), name='specialization-choice-list-create'),
    path('dietitians/by-specialization/<int:specialization_id>/', DietitianListBySpecializationView.as_view(), name='dietitian-list-by-specialization'),
    path('matchings/', MatchingListCreateView.as_view(), name='matching-list-create'),
    path('matchings/<int:pk>/', MatchingRetrieveUpdateDestroyView.as_view(), name='matching-retrieve-update-destroy'),
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroyView.as_view(), name='review-retrieve-update-destroy'),
    path('review/status/<int:pk>/', ReviewStatusView.as_view(),name='review-status'),
] 