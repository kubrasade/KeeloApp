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
from django.contrib.auth import get_user_model
from core.enums import UserType

User= get_user_model()

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

    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'description', 'instructions',
            'difficulty', 'category', 'category_id',
            'video_url', 'image', 'target_muscle_groups',
            'target_muscle_group_ids', 'equipment_needed',
            'equipment_ids', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'approved_by']

class ExerciseListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_muscle = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = ['id', 'name', 'difficulty', 'category_name', 'main_muscle']

    def get_main_muscle(self, obj):
        first_muscle = obj.target_muscle_groups.first()
        return first_muscle.name if first_muscle else None

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseListSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
        write_only=True
    )

    class Meta:
        model = WorkoutExercise
        fields = [
            'id', 'exercise', 'exercise_id', 'sets',
            'reps', 'rest_time', 'order', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
class WorkoutListSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = ['id', 'name', 'difficulty', 'duration', 'average_rating']

    def get_average_rating(self, obj):
        return obj.progress_records.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0

class WorkoutSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, read_only=True)
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
        model = Workout
        fields = [
            'id', 'name', 'description', 'difficulty',
            'duration', 'exercises', 'target_muscle_groups',
            'target_muscle_group_ids', 'equipment_needed',
            'equipment_ids', 'average_rating', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'approved_by']

    def get_average_rating(self, obj):
        return obj.progress_records.filter(rating__isnull=False).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0

class WorkoutPlanDaySerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer(read_only=True)
    workout_id = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(),
        source='workout',
        write_only=True
    )

    class Meta:
        model = WorkoutPlanDay
        fields = [
            'id', 'day_number', 'workout', 'workout_id',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class WorkoutPlanListSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = WorkoutPlan
        fields = ['id', 'name', 'difficulty', 'duration_weeks', 'client']

class WorkoutPlanSerializer(serializers.ModelSerializer):
    plan_days = WorkoutPlanDaySerializer(many=True, read_only=True)
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
    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type=UserType.CLIENT),
        required=False,
        allow_null=True
    )

    class Meta:
        model = WorkoutPlan
        fields = [
            'id', 'name', 'description', 'difficulty',
            'duration_weeks', 'plan_days', 'target_muscle_groups',
            'target_muscle_group_ids', 'equipment_needed',
            'equipment_ids', 'is_personalized', 'client',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'approved_by']

    def validate(self, data):
        if data.get('is_personalized') and not data.get('client'):
            raise serializers.ValidationError("Client must be specified for personalized plans")
        return data

class ProgressSerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer(read_only=True)
    workout_id = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(),
        source='workout',
        write_only=True
    )

    class Meta:
        model = Progress
        fields = [
            'id', 'workout', 'workout_id', 'date',
            'completed', 'notes', 'duration', 'rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def validate(self, data):
        if data.get('completed') and not data.get('duration'):
            raise serializers.ValidationError("Duration is required for completed workouts")
        return data

class PerformanceMetricSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
        write_only=True
    )

    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'exercise', 'exercise_id', 'date',
            'weight', 'reps', 'sets', 'duration',
            'distance', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def validate(self, data):
        exercise = data.get('exercise')
        if not any([data.get('weight'), data.get('reps'), data.get('sets'), data.get('duration'), data.get('distance')]):
            raise serializers.ValidationError("At least one metric (weight, reps, sets, duration, or distance) must be provided")
        return data 







