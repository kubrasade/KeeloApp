from django.db import models
from core.models import BaseModel
from core.enums import Difficulty_Type
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class ExerciseCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='exercise_categories/', null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Exercise Categories'

    def __str__(self):
        return self.name
    
class Exercise(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty_Type.choices)
    category = models.ForeignKey(ExerciseCategory, on_delete=models.CASCADE, related_name='exercises')
    video_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='exercises/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_exercises')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_exercises'
    )
    target_muscle_groups = models.ManyToManyField('MuscleGroup', related_name='exercises')
    equipment_needed = models.ManyToManyField('Equipment', related_name='exercises', blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['difficulty']),
        ]

    def __str__(self):
        return self.name

class MuscleGroup(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='muscle_groups/', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Equipment(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='equipment/', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Workout(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty_Type.choices)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_workouts')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_workouts'
    )
    target_muscle_groups = models.ManyToManyField(MuscleGroup, related_name='workouts')
    equipment_needed = models.ManyToManyField(Equipment, related_name='workouts', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class WorkoutExercise(BaseModel):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    rest_time = models.PositiveIntegerField(help_text="Rest time in seconds")
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ['workout', 'exercise', 'order']

    def __str__(self):
        return f"{self.workout.name} - {self.exercise.name}"
    
class WorkoutPlan(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty_Type.choices)
    duration_weeks = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_plans')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_plans'
    )
    target_muscle_groups = models.ManyToManyField(MuscleGroup, related_name='workout_plans')
    equipment_needed = models.ManyToManyField(Equipment, related_name='workout_plans', blank=True)
    is_personalized = models.BooleanField(default=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='personalized_plans'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class WorkoutPlanDay(BaseModel):
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='plan_days')
    day_number = models.PositiveIntegerField()
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['day_number']
        unique_together = ['plan', 'day_number']

    def __str__(self):
        return f"{self.plan.name} - Day {self.day_number}"

class Progress(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress_records_by_user')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name= 'progress_records')
    date = models.DateField()
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Actual duration in minutes", null=True, blank=True)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'workout', 'date']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.workout.name} - {self.date}"

class PerformanceMetric(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_metrics_by_user')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='performance_metrics')
    date = models.DateField()
    weight = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    sets = models.PositiveIntegerField(null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)
    distance = models.FloatField(help_text="Distance in meters", null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'exercise', 'date']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.exercise.name} - {self.date}" 

