from django.urls import path
from .views import (
    MealCategoryListView,
    IngredientListView,
    RecipeListCreateView,
    RecipeRetrieveUpdateDestroyView,
    RecipeSearchView,
    PopularRecipesView,
    MealPlanListCreateView,
    MealPlanRetrieveUpdateDestroyView,
    RecipeRatingListView,
    RecipeStatisticsView,
    FavoriteRecipeListView,
    AddFavoriteRecipeView,
    RemoveFavoriteRecipeView,
    MacroGoalRetrieveUpdateView,
    DietaryTagListView
)

urlpatterns = [
    path('dietary-tags/', DietaryTagListView.as_view(), name='dietary-tag-list'),
    path('categories/', MealCategoryListView.as_view(), name='meal-category-list'),
    path('ingredients/', IngredientListView.as_view(), name='ingredient-list'),
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list'),
    path('recipes/<int:pk>/', RecipeRetrieveUpdateDestroyView.as_view(), name='recipe-detail'),
    path('recipes/search/', RecipeSearchView.as_view(), name='recipe-search'),
    path('recipes/popular/', PopularRecipesView.as_view(), name='popular-recipes'),
    path('recipes/<int:recipe_id>/ratings/', RecipeRatingListView.as_view(), name='recipe-rating-list'),
    path('recipes/<int:recipe_id>/statistics/', RecipeStatisticsView.as_view(), name='recipe-statistics'),
    path('meal-plans/', MealPlanListCreateView.as_view(), name='meal-plan-list'),
    path('meal-plans/<int:pk>/', MealPlanRetrieveUpdateDestroyView.as_view(), name='meal-plan-detail'),
    path('favorites/', FavoriteRecipeListView.as_view(), name='favorite-list'),
    path('favorites/add/', AddFavoriteRecipeView.as_view(), name='favorite-add'),
    path('favorites/remove/<int:recipe_id>/', RemoveFavoriteRecipeView.as_view(), name='favorite-remove'),
    path('macro-goal/', MacroGoalRetrieveUpdateView.as_view(), name='macro-goal'),
] 
