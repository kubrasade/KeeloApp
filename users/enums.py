from django.db import models

class FitnessLevel(models.IntegerChoices):
    LOW= 1, "Low"
    MEDIUM = 2, 'Medium'
    HIGH = 3, 'High'

class HealthMetricType(models.IntegerChoices):
    WEIGHT = 1, ('Weight')
    BODY_FAT = 2, ('Body Fat')
    HEIGHT = 3, ('Height')
    BMI = 4, ('Body Mass Index')
    WAIST = 5, ('Waist Circumference')
    HIP = 6, ('Hip Circumference')
    CHEST = 7, ('Chest Circumference')
    ARM = 8, ('Arm Circumference')
    THIGH = 9, ('Thigh Circumference')
    WATER = 10, ('Water Intake')
    SLEEP = 11, ('Sleep Duration')
    STEPS = 12, ('Step Count')