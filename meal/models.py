from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel

class DietaryTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MealCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='meal_categories/', null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Meal Categories'

    def __str__(self):
        return self.name