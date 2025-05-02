from .models import (
    Exercise,
    Workout,
    WorkoutPlan,
    WorkoutPlanDay,
    Progress,
    PerformanceMetric
)
from django.db.models import Avg, Count, Q, F, ExpressionWrapper, FloatField, Max
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
            usage_count=Count('performance_metrics')
        ).filter(
            usage_count__gt=0
        ).order_by('-usage_count')[:limit]

        cache.set(cache_key, exercises, settings.CACHE_TTL)
        return exercises

    @staticmethod
    def approve_exercise(user, exercise):
        if not (user.is_staff or user.user_type in [UserType.DIETITIAN, UserType.ADMIN]):
            raise exceptions.PermissionDenied("Only dietitians or admins can approve exercises.")
        exercise.approved_by = user
        exercise.save()
        return exercise
    
class WorkoutService:
    @staticmethod
    def create_workout(user, data):
        workout = Workout.objects.create(created_by=user, **data)
        return workout

    @staticmethod
    def get_recommended_workouts(user, limit=5, filters=None):
        cache_key = f'recommended_workouts_{user.id}_{limit}'
        cached_workouts = cache.get(cache_key)
        if cached_workouts:
            return cached_workouts

        fitness_level = getattr(user, 'fitness_level', 1)

        workouts = Workout.objects.filter(
            approved_by__isnull=False,
            difficulty__lte=fitness_level + 1
        )

        if filters:
            if filters.get('difficulty'):
                workouts = workouts.filter(difficulty=filters['difficulty'])

        workouts = workouts.annotate(
            rating_count=Count('progress_records'),
            avg_rating=Avg('progress_records__rating')
        ).filter(
            rating_count__gt=0
        ).order_by(
            '-avg_rating', '-rating_count'
        )[:limit]

        cache.set(cache_key, workouts, settings.CACHE_TTL)
        return workouts

class WorkoutPlanService:
    @staticmethod
    def create_personalized_plan(user, client, data):
        if not (user.is_staff or user.user_type in [UserType.DIETITIAN, UserType.ADMIN]):
            raise exceptions.PermissionDenied("Only dietitians or admins can create personalized plans.")

        data['is_personalized'] = True
        data['client'] = client
        plan = WorkoutPlan.objects.create(created_by=user, **data)
        return plan

    @staticmethod
    def get_client_plans(client):
        return WorkoutPlan.objects.filter(
            Q(client=client) | Q(is_personalized=False)
        ).order_by('-created_at')

    @staticmethod
    def get_weekly_schedule(plan, week_number):
        start_day = (week_number - 1) * 7 + 1
        end_day = start_day + 6

        return WorkoutPlanDay.objects.filter(
            plan=plan,
            day_number__range=(start_day, end_day)
        ).order_by('day_number')

class ProgressService:
    @staticmethod
    def record_workout_progress(user, workout, data):
        if Progress.objects.filter(user=user, workout=workout, date=data['date']).exists():
            raise exceptions.ValidationError("Progress for this workout and date already exists.")
        
        data = dict(data)  
        data.pop('workout', None)
        
        return Progress.objects.create(user=user, workout=workout, **data)

    @staticmethod
    def get_workout_history(user, start_date=None, end_date=None):
        queryset = Progress.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset.order_by('-date')

class PerformanceMetricService:
    @staticmethod
    def record_metric(user, exercise, data):
        data.pop('exercise', None)  
        data.pop('user', None)      
        return PerformanceMetric.objects.create(user=user, exercise=exercise, **data)

    @staticmethod
    def get_exercise_progress(user, exercise, start_date=None, end_date=None):
        queryset = PerformanceMetric.objects.filter(user=user, exercise=exercise)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset.order_by('date')

    @staticmethod
    def calculate_progress_stats(user, exercise):
        metrics = PerformanceMetric.objects.filter(user=user, exercise=exercise)
        if not metrics.exists():
            return None

        return {
            'total_workouts': metrics.count(),
            'max_weight': metrics.aggregate(max_weight=Max('weight'))['max_weight'],
            'max_reps': metrics.aggregate(max_reps=Max('reps'))['max_reps'],
            'avg_weight': metrics.aggregate(avg_weight=Avg('weight'))['avg_weight'],
            'avg_reps': metrics.aggregate(avg_reps=Avg('reps'))['avg_reps'],
            'last_workout': metrics.order_by('-date').first().date
        }
    