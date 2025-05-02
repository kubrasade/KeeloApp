from django.urls import path
from .views import (
    ExerciseListView,
    ExerciseSearchView,
    PopularExercisesView,
    WorkoutListView,
    RecommendedWorkoutsView
)

urlpatterns = [
    path('exercises/', ExerciseListView.as_view(), name='exercise-list'),
    path('exercises/search/', ExerciseSearchView.as_view(), name='exercise-search'),
    path('exercises/popular/', PopularExercisesView.as_view(), name='popular-exercise'),

    path('workout/', WorkoutListView.as_view(), name='workout-list-create'),
    path('workout/recommended/', RecommendedWorkoutsView.as_view(), name='recommended-workout')

    

]