from django.db import models
from core.models import BaseModel

class ExerciseCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='exercise_categories/', null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Exercise Categories'

    def __str__(self):
        return self.name