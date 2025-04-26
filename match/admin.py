from django.contrib import admin
from .models import MatchModel, Review, SpecializationChoice

admin.site.register(MatchModel)
admin.site.register(Review)
admin.site.register(SpecializationChoice)
