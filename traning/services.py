from .models import (
    Exercise,
    Workout,
    WorkoutPlan,
    WorkoutPlanDay,
    Progress,
    PerformanceMetric
)
from django.db.models import Avg, Count, Q, F, ExpressionWrapper, FloatField
from django.core.cache import cache
from django.conf import settings
from rest_framework import exceptions
from django.utils import timezone
from datetime import timedelta
from core.enums import UserType

class ExerciseService:
    @staticmethod
    def search_exercises(query, filters=None):
        cache_key = f'exercise_search_{query}_{filters}'
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return cached_results

        queryset = Exercise.objects.all()
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(instructions__icontains=query)
            )
        
        if filters:
            if filters.get('category'):
                queryset = queryset.filter(category_id=filters['category'])
            if filters.get('difficulty'):
                queryset = queryset.filter(difficulty=filters['difficulty'])
            if filters.get('muscle_group'):
                queryset = queryset.filter(target_muscle_groups__id=filters['muscle_group'])
            if filters.get('equipment'):
                queryset = queryset.filter(equipment_needed__id=filters['equipment'])

        results = list(queryset)
        cache.set(cache_key, results, settings.CACHE_TTL)
        return results

    @staticmethod
    def get_popular_exercises(limit=10):
        cache_key = f'popular_exercises_{limit}'
        cached_exercises = cache.get(cache_key)
        if cached_exercises:
            return cached_exercises
    
        exercises = Exercise.objects.annotate(
            rating_count=Count('progress_records'),
            avg_rating=Avg('progress_records__rating')
        ).filter(
            rating_count__gt=0
        ).order_by(
            '-avg_rating', '-rating_count'
        )[:limit]
    
        cache.set(cache_key, exercises, settings.CACHE_TTL)
        return exercises

    @staticmethod
    def approve_exercise(user, exercise):
        if not (user.is_staff or user.user_type in [UserType.DIETITIAN, UserType.ADMIN]):
            raise exceptions.PermissionDenied("Only dietitians or admins can approve exercises.")
        exercise.approved_by = user
        exercise.save()
        return exercise