from django.contrib import admin
from .models import (
    ExerciseCategory,
    Exercise,
    MuscleGroup,
    Equipment,
    Workout,
    WorkoutExercise,
    WorkoutPlan,
    WorkoutPlanDay,
    Progress,
    PerformanceMetric
)

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'category', 'created_by', 'approved_by']
    list_filter = ['difficulty', 'category']
    search_fields = ['name', 'description']
    filter_horizontal = ['target_muscle_groups', 'equipment_needed']

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'duration', 'created_by', 'approved_by']
    list_filter = ['difficulty']
    search_fields = ['name']
    filter_horizontal = ['target_muscle_groups', 'equipment_needed']

@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'sets', 'reps', 'order']
    list_filter = ['workout', 'exercise']

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'duration_weeks', 'is_personalized', 'client']
    list_filter = ['difficulty', 'is_personalized']
    search_fields = ['name']
    filter_horizontal = ['target_muscle_groups', 'equipment_needed']

@admin.register(WorkoutPlanDay)
class WorkoutPlanDayAdmin(admin.ModelAdmin):
    list_display = ['plan', 'day_number', 'workout']
    list_filter = ['plan']
    search_fields = ['plan__name']

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout', 'date', 'completed', 'rating']
    list_filter = ['completed', 'date']
    search_fields = ['user__first_name', 'workout__name']

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'date', 'weight', 'reps', 'sets']
    search_fields = ['user__first_name', 'exercise__name']
    list_filter = ['date']