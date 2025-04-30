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




