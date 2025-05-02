from django.urls import path
from .views import (
    ExerciseListView,
    ExerciseSearchView
)

urlpatterns = [
    path('exercises/', ExerciseListView.as_view(), name='exercise-list'),
    path('exercises/search/', ExerciseSearchView.as_view(), name='exercise-search'),

]