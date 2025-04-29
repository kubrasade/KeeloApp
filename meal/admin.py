from django.contrib import admin
from .models import DietaryTag, MealCategory, Ingredient, Recipe, RecipeIngredient, MealPlan, RecipeRating, FavoriteRecipe, MacroGoal

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(DietaryTag)
class DietaryTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(MealCategory)
class MealCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'difficulty', 'meal_type', 'created_at', 'approved_by')
    search_fields = ('title', 'description')
    list_filter = ('difficulty', 'meal_type', 'category', 'dietary_tags')
    ordering = ('-created_at',)
    inlines = [RecipeIngredientInline]  
    autocomplete_fields = ['category', 'created_by', 'approved_by', 'dietary_tags']

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'day', 'meal_type', 'recipe', 'date')
    list_filter = ('day', 'meal_type', 'date')
    search_fields = ('user__first_name', 'user__last_name', 'recipe__title')
    ordering = ('date',)
