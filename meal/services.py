from .models import (
    MealCategory,
    Ingredient,
    Recipe,
    RecipeIngredient,
    MealPlan,
    RecipeRating,
    FavoriteRecipe,
    MacroGoal,
)
from django.db.models import Avg, Count, Q, Sum, F, ExpressionWrapper, FloatField
from django.core.cache import cache
from django.conf import settings
from rest_framework import exceptions
from django.utils import timezone
from datetime import timedelta

class RecipeService:
    @staticmethod
    def search_recipes(query, filters=None):
        cache_key = f'recipe_search_{query}_{filters}'
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return cached_results

        queryset = Recipe.objects.all()
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(instructions__icontains=query)
            )
        
        if filters:
            if filters.get('category'):
                queryset = queryset.filter(category_id=filters['category'])
            if filters.get('meal_type'):
                queryset = queryset.filter(meal_type=filters['meal_type'])
            if filters.get('difficulty'):
                queryset = queryset.filter(difficulty=filters['difficulty'])
            if filters.get('min_rating'):
                queryset = queryset.annotate(
                    avg_rating=Avg('ratings__rating')
                ).filter(avg_rating__gte=filters['min_rating'])
            if filters.get('max_calories'):
                queryset = queryset.annotate(
                    total_calories=Sum(
                        ExpressionWrapper(
                            F('ingredients__quantity') * F('ingredients__ingredient__calories_per_100g') / 100,
                            output_field=FloatField()
                        )
                    )
                ).filter(total_calories__lte=filters['max_calories'])

        results = list(queryset)
        cache.set(cache_key, results, settings.CACHE_TTL)
        return results

    @staticmethod
    def get_popular_recipes(limit=10):
        cache_key = f'popular_recipes_{limit}'
        cached_recipes = cache.get(cache_key)
        
        if cached_recipes:
            return cached_recipes

        recipes = Recipe.objects.annotate(
            rating_count=Count('ratings'),
            avg_rating=Avg('ratings__rating')
        ).order_by('-rating_count', '-avg_rating')[:limit]

        cache.set(cache_key, recipes, settings.CACHE_TTL)
        return recipes

class MealPlanService:
    @staticmethod
    def create_meal_plan(user, data):
        if MealPlan.objects.filter(
            user=user,
            day=data['day'],
            meal_type=data['meal_type'],
            date=data['date']
        ).exists():
            raise exceptions.ValidationError("There is already a plan for this meal.")
        
        return MealPlan.objects.create(user=user, **data)

    @staticmethod
    def get_weekly_meal_plan(user, start_date):
        end_date = start_date + timedelta(days=6)
        return MealPlan.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date', 'meal_type')

    @staticmethod
    def get_daily_calories(user, date):
        meal_plans = MealPlan.objects.filter(user=user, date=date)
        total_calories = sum(meal_plan.recipe.total_calories for meal_plan in meal_plans)
        return total_calories


