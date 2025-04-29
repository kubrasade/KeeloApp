from django.db import models 

class Meal_Type(models.IntegerChoices):
    BREAKFAST= 1, "Breakfast"
    LUNCH= 2, "Lunch"
    DINNER= 3, "Dinner"
    SNACK= 4, "Snack"

