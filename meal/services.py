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
from core.enums import UserType

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
        ).filter(
            rating_count__gt=0
        ).order_by(
            '-avg_rating', '-rating_count'
        )[:limit]
    
        cache.set(cache_key, recipes, settings.CACHE_TTL)
        return recipes

    @staticmethod
    def approve_recipe(user, recipe):
        if not (user.is_staff or user.user_type in [UserType.DIETITIAN, UserType.ADMIN]):
            raise exceptions.PermissionDenied("Only dietitians or admins can approve recipes.")
        recipe.approved_by = user
        recipe.save()
        return recipe

class MealPlanService:
    @staticmethod
    def create_meal_plan(request_user, data):
        user = data.pop('user', None) or request_user
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


class RecipeRatingService:
    @staticmethod
    def create_rating(user, recipe, data):
        if RecipeRating.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError("You have already reviewed this recipe.")
        
        return RecipeRating.objects.create(user=user, recipe=recipe, **data)

    @staticmethod
    def get_recipe_statistics(recipe):
        ratings = RecipeRating.objects.filter(recipe=recipe)
        total_ratings = ratings.count()
        
        if total_ratings == 0:
            return {
                'average_rating': 0,
                'rating_count': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        rating_distribution = ratings.values('rating').annotate(count=Count('rating'))
        distribution_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for item in rating_distribution:
            distribution_dict[item['rating']] = item['count']
        
        return {
            'average_rating': ratings.aggregate(avg=Avg('rating'))['avg'],
            'rating_count': total_ratings,
            'rating_distribution': distribution_dict
        }

class FavoriteRecipeService:
    @staticmethod
    def add_to_favorites(user, recipe):
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError("This recipe has already been added to your favorites.")
        return FavoriteRecipe.objects.create(user=user, recipe=recipe)

    @staticmethod
    def remove_from_favorites(user, recipe):
        favorite = FavoriteRecipe.objects.filter(user=user, recipe=recipe).first()
        if not favorite:
            raise exceptions.ValidationError("This recipe was not found in your favorites.")
        favorite.delete()
        return

    @staticmethod
    def get_user_favorites(user):
        return FavoriteRecipe.objects.filter(user=user).select_related('recipe')

class MacroGoalService:
    @staticmethod
    def get_user_macro_goal(user):
        return getattr(user, 'macro_goal', None)


    @staticmethod
    def update_macro_goal(user, data):
        defaults = {
            'daily_calories': 2000,
            'daily_protein': 100,
            'daily_carbs': 250,
            'daily_fat': 70,
        }

        macro_goal, created = MacroGoal.objects.get_or_create(
            user=user,
            defaults=defaults
        )

        if not created:
            for field, default_value in defaults.items():
                value = data.get(field, getattr(macro_goal, field, default_value))
                setattr(macro_goal, field, value)
            macro_goal.save()

        return macro_goal