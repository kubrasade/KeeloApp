from rest_framework import serializers
from .models import MatchModel, Review, SpecializationChoice
from users.serializers import  SpecializationSerializer
from users.models import DietitianProfile, ClientProfile, Specialization
from django.db.models import Avg
from core.enums import MatchingStatus, ReviewStatus
from .services import MatchingService, ReviewService
from django.contrib.auth import get_user_model

User= get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

class SimpleClientProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = ('id', 'user')

class SimpleDietitianProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = DietitianProfile
        fields = ('id', 'user', 'specializations', 'experience_years')
