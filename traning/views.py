from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Exercise,
    Workout,
)
from .serializers import (
    ExerciseSerializer,
    ExerciseListSerializer,
    WorkoutListSerializer,
    WorkoutSerializer
)
from .services import (
    ExerciseService,
    WorkoutService
)

from core.enums import UserType

from core.enums import UserType


class ExerciseListView(generics.ListAPIView):
    serializer_class = ExerciseListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'difficulty']
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.user_type == UserType.ADMIN:
            return Exercise.objects.all()
        return Exercise.objects.filter(approved_by__isnull=False)


class ExerciseSearchView(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        filters = {
            'category': self.request.query_params.get('category'),
            'difficulty': self.request.query_params.get('difficulty'),
            'muscle_group': self.request.query_params.get('muscle_group'),
            'equipment': self.request.query_params.get('equipment'),
        }
        return ExerciseService.search_exercises(query, filters)


class PopularExercisesView(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 10))
        return ExerciseService.get_popular_exercises(limit)


class WorkoutListView(generics.ListCreateAPIView):
    serializer_class = WorkoutListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['difficulty']
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.user_type == UserType.ADMIN:
            return Workout.objects.all()
        return Workout.objects.filter(approved_by__isnull=False)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RecommendedWorkoutsView(generics.ListAPIView):
    serializer_class = WorkoutListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 5))
        filters = {
            'difficulty': self.request.query_params.get('difficulty')
        }
        return WorkoutService.get_recommended_workouts(self.request.user, limit, filters)


