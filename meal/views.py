from django.shortcuts import render
from rest_framework import generics, status, filters, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    MealCategory,
    Ingredient,
    Recipe,
    RecipeIngredient,
    MealPlan,
    RecipeRating
)
from .serializers import (
    MealCategorySerializer,
    IngredientSerializer,
    RecipeSerializer,
    MealPlanSerializer,
    RecipeRatingSerializer,
    FavoriteRecipeSerializer,
    MacroGoalSerializer
)
from .services import (
    RecipeService,
    MealPlanService,
    RecipeRatingService,
    FavoriteRecipeService,
    MacroGoalService
)
from django.utils import timezone
from datetime import datetime, timedelta
from core.enums import UserType


class MealCategoryListView(generics.ListAPIView):
    queryset = MealCategory.objects.all()
    serializer_class = MealCategorySerializer
    permission_classes = [IsAuthenticated]

class IngredientListView(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class RecipeListCreateView(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'meal_type', 'difficulty']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.user_type == UserType.ADMIN:
            return Recipe.objects.all()
        return Recipe.objects.filter(approved_by__isnull=False)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RecipeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user= self.request.user
        if user.is_staff or user.user_type == UserType.DIETITIAN:
            return Recipe.objects.all()
        return Recipe.objects.filter(created_by=self.request.user)
    
class RecipeSearchView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        filters = {
            'category': self.request.query_params.get('category'),
            'meal_type': self.request.query_params.get('meal_type'),
            'difficulty': self.request.query_params.get('difficulty'),
            'min_rating': self.request.query_params.get('min_rating'),
            'max_calories': self.request.query_params.get('max_calories'),
        }
        return RecipeService.search_recipes(query, filters)

class ApproveRecipeView(generics.UpdateAPIView):
    serializer_class= RecipeSerializer
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(approved_by__isnull=True)
    
    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        RecipeService.approve_recipe(request.user, recipe)
        return Response({"detail": "Recipe approved successfully."}, status=200)


class PopularRecipesView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 10))
        return RecipeService.get_popular_recipes(limit)

class MealPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                return MealPlanService.get_weekly_meal_plan(self.request.user, start_date)
            except ValueError:
                return MealPlan.objects.none()
        return MealPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        MealPlanService.create_meal_plan(self.request.user, serializer.validated_data)

class MealPlanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user)

class RecipeRatingListView(generics.ListCreateAPIView):
    serializer_class = RecipeRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return RecipeRating.objects.filter(recipe_id=recipe_id)

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = Recipe.objects.get(id=recipe_id)

        if RecipeRating.objects.filter(user=self.request.user, recipe=recipe).exists():
            raise serializers.ValidationError("You have already reviewed this recipe.")

        serializer.save(user=self.request.user, recipe=recipe)

class RecipeStatisticsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = Recipe.objects.get(id=recipe_id)
        statistics = RecipeRatingService.get_recipe_statistics(recipe)
        return Response(statistics)

class FavoriteRecipeListView(generics.ListAPIView):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteRecipeService.get_user_favorites(self.request.user)

class AddFavoriteRecipeView(generics.CreateAPIView):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        recipe = serializer.validated_data['recipe']
        FavoriteRecipeService.add_to_favorites(self.request.user, recipe)

class RemoveFavoriteRecipeView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'recipe_id'

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = Recipe.objects.get(id=recipe_id)
        FavoriteRecipeService.remove_from_favorites(self.request.user, recipe)
        return recipe

class MacroGoalRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = MacroGoalSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        macro_goal = MacroGoalService.get_user_macro_goal(self.request.user)

        if not macro_goal:
            macro_goal = MacroGoalService.update_macro_goal(self.request.user, {})

        return macro_goal