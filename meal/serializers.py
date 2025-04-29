from rest_framework import serializers
from .models import (
    MealCategory,
    Ingredient,
    Recipe,
    RecipeIngredient,
    MealPlan,
    RecipeRating,
    DietaryTag,
    FavoriteRecipe,
    MacroGoal,
)
from django.db.models import Avg

class MealCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCategory
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
