from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from core.enums import UserType
from rest_framework.exceptions import PermissionDenied
from .models import (
    Exercise,
    Workout,
    WorkoutPlan,
)
from .serializers import (
    ExerciseSerializer,
    ExerciseListSerializer,
    WorkoutListSerializer,
    WorkoutSerializer,
    WorkoutPlanSerializer,
    WorkoutPlanListSerializer,
    WorkoutPlanDaySerializer,
)
from .services import (
    ExerciseService,
    WorkoutService,
    WorkoutPlanService,
)


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

class WorkoutPlanListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return WorkoutPlanListSerializer if self.request.method == 'GET' else WorkoutPlanSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.user_type == UserType.ADMIN:
            return WorkoutPlan.objects.all()

        if user.user_type == UserType.DIETITIAN:
            return WorkoutPlan.objects.filter(created_by=user)

        if user.user_type == UserType.CLIENT:
            return WorkoutPlanService.get_client_plans(user)

        return WorkoutPlan.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type == UserType.CLIENT:
            serializer.save(
                created_by=user,
                client=user,
                is_personalized=False
            )
        else:
            serializer.save(created_by=user)

class WorkoutPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.user_type == UserType.ADMIN:
            return WorkoutPlan.objects.all()

        if user.user_type == UserType.DIETITIAN:
            return WorkoutPlan.objects.filter(created_by=user)

        if user.user_type == UserType.CLIENT:
            return WorkoutPlan.objects.filter(client=user)

        return WorkoutPlan.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        if (
            user.user_type == UserType.ADMIN
            or (user.user_type == UserType.DIETITIAN and instance.created_by == user)
            or (user.user_type == UserType.CLIENT and instance.client == user)
        ):
            serializer.save()
        else:
            raise PermissionDenied("You don't have permission to update this plan.")

    def perform_destroy(self, instance):
        user = self.request.user

        if (
            user.user_type == UserType.ADMIN
            or (user.user_type == UserType.DIETITIAN and instance.created_by == user)
            or (user.user_type == UserType.CLIENT and instance.client == user)
        ):
            instance.delete()
        else:
            raise PermissionDenied("You don't have permission to delete this plan.")
           
class WeeklyScheduleView(generics.ListAPIView):
    serializer_class = WorkoutPlanDaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        plan_id = self.kwargs.get('plan_id')
        plan = get_object_or_404(WorkoutPlan, id=plan_id)

        try:
            week_number = int(self.request.query_params.get('week', 1))
        except ValueError:
            week_number = 1

        return WorkoutPlanService.get_weekly_schedule(plan, week_number)


















