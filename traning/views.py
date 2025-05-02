from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Exercise,
)
from .serializers import (
    ExerciseSerializer,
    ExerciseListSerializer
)
from .services import (
    ExerciseService,
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










