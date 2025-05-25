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
from users.models import User

class DietaryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryTag
        fields = ['id', 'name']

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

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'ingredient_id', 'quantity', 'unit', 'unit_display', 'notes']
        read_only_fields = ['id']
    
class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'image']
        
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, required=False)
    category = MealCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=MealCategory.objects.all(),
        source='category',
        write_only=True
    )
    dietary_tags = DietaryTagSerializer(many=True, read_only=True)
    dietary_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=DietaryTag.objects.all(),
        source='dietary_tags',
        write_only=True,
        many=True
    )
    total_calories = serializers.FloatField(read_only=True)
    total_protein = serializers.FloatField(read_only=True)
    total_carbs = serializers.FloatField(read_only=True)
    total_fat = serializers.FloatField(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions',
            'preparation_time', 'cooking_time', 'servings',
            'difficulty', 'meal_type', 'image', 'video_url',
            'category', 'category_id',
            'ingredients', 'dietary_tags', 'dietary_tag_ids',
            'total_calories', 'total_protein', 'total_carbs', 'total_fat',
            'average_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def get_average_rating(self, obj):
        return obj.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        dietary_tags_data = validated_data.pop('dietary_tags', [])

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)

        if dietary_tags_data:
            recipe.dietary_tags.set(dietary_tags_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(recipe=instance, **ingredient_data)

        return instance
    
class MealPlanSerializer(serializers.ModelSerializer):
    recipe = RecipeListSerializer(read_only=True)
    recipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        source='recipe',
        write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    class Meta:
        model = MealPlan
        fields = [
            'id', 'day', 'meal_type', 'recipe', 'recipe_id',
            'date', 'notes', 'created_at', 'updated_at', 'user', 'user_id'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def validate(self, data):
        if MealPlan.objects.filter(
            user=self.context['request'].user,
            day=data['day'],
            meal_type=data['meal_type'],
            date=data['date']
        ).exists():
            raise serializers.ValidationError("There is already a plan for this meal.")
        return data

class RecipeRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeRating
        fields = ['id', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'user', 'recipe']

        
class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeListSerializer(read_only=True)
    recipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        source='recipe',
        write_only=True
    )

    class Meta:
        model = FavoriteRecipe
        fields = ['id', 'recipe', 'recipe_id', 'added_at']
        read_only_fields = ['added_at']

class MacroGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MacroGoal
        fields = [
            'id', 'daily_calories', 'daily_protein',
            'daily_carbs', 'daily_fat', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

