from django.db import models
from core.models import BaseModel
from core.enums import Difficulty_Type
from django.conf import settings

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


