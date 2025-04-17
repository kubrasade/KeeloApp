from django.db import models

class FitnessLevel(models.IntegerChoices):
    LOW= 1, "Low"
    MEDIUM = 2, 'Medium'
    HIGH = 3, 'High'