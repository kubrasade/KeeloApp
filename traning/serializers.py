from rest_framework import serializers
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
from django.db.models import Avg

class MuscleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']




