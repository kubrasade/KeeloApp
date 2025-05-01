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

class ExerciseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseCategory
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ExerciseSerializer(serializers.ModelSerializer):
    category = ExerciseCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ExerciseCategory.objects.all(),
        source='category',
        write_only=True
    )
    target_muscle_groups = MuscleGroupSerializer(many=True, read_only=True)
    target_muscle_group_ids = serializers.PrimaryKeyRelatedField(
        queryset=MuscleGroup.objects.all(),
        source='target_muscle_groups',
        write_only=True,
        many=True
    )
    equipment_needed = EquipmentSerializer(many=True, read_only=True)
    equipment_ids = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        source='equipment_needed',
        write_only=True,
        many=True
    )
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'description', 'instructions',
            'difficulty', 'category', 'category_id',
            'video_url', 'image', 'target_muscle_groups',
            'target_muscle_group_ids', 'equipment_needed',
            'equipment_ids', 'average_rating', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'approved_by']













