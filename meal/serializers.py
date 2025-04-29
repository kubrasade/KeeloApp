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

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'description',
            'calories_per_100g', 'protein_per_100g',
            'carbs_per_100g', 'fat_per_100g',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class DietaryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryTag
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']



