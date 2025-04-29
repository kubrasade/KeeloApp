from django.db import models 

class Meal_Type(models.IntegerChoices):
    BREAKFAST= 1, "Breakfast"
    LUNCH= 2, "Lunch"
    DINNER= 3, "Dinner"
    SNACK= 4, "Snack"

class Unit_Type(models.IntegerChoices):
    G= 1, "Gram"
    ML= 2, "Milliliter"
    PIECE= 3, "Piece"
