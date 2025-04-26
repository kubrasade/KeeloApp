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

class SimpleMatchingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchModel
        fields = ['id']

class DietitianScoreSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = DietitianProfile
        fields = [
            'id', 'user', 'specializations', 'experience_years',
            'average_rating', 'review_count', 'total_score'
        ]

    def get_average_rating(self, obj):
        return Review.objects.filter(matching__dietitian=obj).aggregate(avg=Avg('rating'))['avg'] or 0

    def get_review_count(self, obj):
        return Review.objects.filter(matching__dietitian=obj).count()

    def get_total_score(self, obj):
        avg_rating = self.get_average_rating(obj)
        experience_years = obj.experience_years or 0
        review_count = self.get_review_count(obj)

        normalized_experience = min(experience_years / 30, 1)
        normalized_reviews = min(review_count / 100, 1)

        return (
            (avg_rating / 5) * 0.4 +
            normalized_experience * 0.3 +
            normalized_reviews * 0.3
        ) * 100

class SpecializationChoiceSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    specialization_id = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        source='specialization',
        write_only=True
    )

    class Meta:
        model = SpecializationChoice
        fields = ['id', 'specialization', 'specialization_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        client = self.context['request'].user.client_profile
        if SpecializationChoice.objects.filter(client=client, specialization=data['specialization']).exists():
            raise serializers.ValidationError("You have already selected this specialization.")
        return data
