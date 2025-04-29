from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from core.enums import Difficulty_Type, Day_Choices
from .enums import Meal_Type, Unit_Type

class DietaryTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MealCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='meal_categories/', null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Meal Categories'

    def __str__(self):
        return self.name

class Ingredient(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    calories_per_100g = models.FloatField(validators=[MinValueValidator(0)])
    protein_per_100g = models.FloatField(validators=[MinValueValidator(0)])
    carbs_per_100g = models.FloatField(validators=[MinValueValidator(0)])
    fat_per_100g = models.FloatField(validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    preparation_time = models.PositiveIntegerField(help_text="Preparation time (minutes)")
    cooking_time = models.PositiveIntegerField(help_text="Cooking time (minutes)")
    servings = models.PositiveIntegerField()
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty_Type.choices)
    meal_type = models.PositiveSmallIntegerField(choices=Meal_Type.choices)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    video_url = models.URLField(blank=True, null=True, help_text="Video Link (YouTube vb.)") 
    category = models.ForeignKey(MealCategory, on_delete=models.CASCADE, related_name='recipes')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    approved_by = models.ForeignKey(  
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_recipes'
    )
    dietary_tags = models.ManyToManyField(DietaryTag, blank=True, related_name='recipes')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['category']),
            models.Index(fields=['meal_type']),
            models.Index(fields=['difficulty']),
        ]

    def __str__(self):
        return self.title

    @property
    def total_calories(self):
        return sum(ingredient.quantity * ingredient.ingredient.calories_per_100g / 100 
                  for ingredient in self.ingredients.all())

    @property
    def total_protein(self):
        return sum(ingredient.quantity * ingredient.ingredient.protein_per_100g / 100 
                  for ingredient in self.ingredients.all())

    @property
    def total_carbs(self):
        return sum(ingredient.quantity * ingredient.ingredient.carbs_per_100g / 100 
                  for ingredient in self.ingredients.all())

    @property
    def total_fat(self):
        return sum(ingredient.quantity * ingredient.ingredient.fat_per_100g / 100 
                  for ingredient in self.ingredients.all())

    @property
    def estimated_total_time(self):
        return self.preparation_time + self.cooking_time
    

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.PositiveSmallIntegerField( choices=Unit_Type.choices)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['recipe', 'ingredient']

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.name}"

class MealPlan(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans')
    day = models.PositiveSmallIntegerField(choices=Day_Choices.choices)
    meal_type = models.PositiveSmallIntegerField(choices=Meal_Type.choices)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['user', 'day', 'meal_type', 'date']
        ordering = ['date', 'meal_type']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_day_display()} - {self.get_meal_type_display()}"


class RecipeRating(BaseModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ['recipe', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.recipe.title} - {self.rating}"
    
class FavoriteRecipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']