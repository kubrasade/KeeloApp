from django.urls import path
from .views import (
    ExerciseListView,
    ExerciseSearchView,
    PopularExercisesView,
    WorkoutListView,
    RecommendedWorkoutsView,
    WorkoutPlanListView,
    WorkoutPlanDetailView,
    WeeklyScheduleView,
    ProgressListView,
    PerformanceMetricListView,
    ExerciseProgressView,
    ProgressUpdateDeleteView
)

urlpatterns = [
    path('exercises/', ExerciseListView.as_view(), name='exercise-list'),
    path('exercises/search/', ExerciseSearchView.as_view(), name='exercise-search'),
    path('exercises/popular/', PopularExercisesView.as_view(), name='popular-exercise'),

    path('workout/', WorkoutListView.as_view(), name='workout-list-create'),
    path('workout/recommended/', RecommendedWorkoutsView.as_view(), name='recommended-workout'),

    path('workoutplan/', WorkoutPlanListView.as_view(), name="workoutplan-list-create"), 
    path('workoutplan/detail/<int:pk>/', WorkoutPlanDetailView.as_view(), name= 'workoutplan-detail'),  
    path('workplan/<int:plan_id>/schedule/', WeeklyScheduleView.as_view(), name='weekly-schedule'),

    path('progress/', ProgressListView.as_view(), name='progress-list-create'),
    path('progress/<int:pk>/', ProgressUpdateDeleteView.as_view(), name="update-progress"),

    path('exercises/<int:exercise_id>/metrics/', PerformanceMetricListView.as_view(), name='exercise-metrics'),
    path('exercises/<int:exercise_id>/progress/', ExerciseProgressView.as_view(), name='exercise-progress'),
]