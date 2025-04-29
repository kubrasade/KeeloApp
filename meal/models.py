from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class DietaryTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
