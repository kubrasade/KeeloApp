from rest_framework import serializers
from .models import MatchModel, Review, SpecializationChoice
from users.serializers import  SpecializationSerializer
from users.models import DietitianProfile, ClientProfile, Specialization
from django.db.models import Avg
from core.enums import MatchingStatus, ReviewStatus
from .services import MatchingService, ReviewService
from django.contrib.auth import get_user_model
from notifications.services import NotificationService

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

class MatchingSerializer(serializers.ModelSerializer):
    client = SimpleClientProfileSerializer(read_only=True)
    dietitian = DietitianScoreSerializer(read_only=True)
    specialization = SpecializationSerializer(read_only=True)

    client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all(), source='client', write_only=True)
    dietitian_id = serializers.PrimaryKeyRelatedField(queryset=DietitianProfile.objects.all(), source='dietitian', write_only=True)
    specialization_id = serializers.PrimaryKeyRelatedField(queryset=Specialization.objects.all(), source='specialization', write_only=True)

    class Meta:
        model = MatchModel
        fields = [
            'id', 'client', 'dietitian', 'specialization',
            'client_id', 'dietitian_id', 'specialization_id',
            'status', 'created_at', 'updated_at', 'matched_at', 'ended_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'matched_at', 'ended_at']

    def create(self, validated_data):
        return MatchingService.create_matching(**validated_data)
    
class MatchingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchModel
        fields = ['status']

    def validate_status(self, value):
        if value not in [MatchingStatus.ACCEPTED, MatchingStatus.REJECTED, MatchingStatus.ENDED]:
            raise serializers.ValidationError("Invalid status.")
        return value

    def update(self, instance, validated_data):
        return MatchingService.update_matching_status(instance, validated_data['status'])

class ReviewSerializer(serializers.ModelSerializer):
    matching = SimpleMatchingSerializer(read_only=True)
    matching_id = serializers.PrimaryKeyRelatedField(
        queryset=MatchModel.objects.filter(status=MatchingStatus.ACCEPTED),
        source='matching',
        write_only=True
    )

    class Meta:
        model = Review
        fields = ['id', 'matching', 'matching_id', 'rating', 'comment', 'created_at', 'updated_at', 'status']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']

    def validate(self, data):
        matching = data['matching']
        user = self.context['request'].user

        if matching.client.user != user:
            raise serializers.ValidationError("You can only review your own dietitian.")

        if Review.objects.filter(matching=matching).exists():
            raise serializers.ValidationError("You have already submitted a review for this match.")
        return data

    def create(self, validated_data):
        return ReviewService.create_review(
            matching=validated_data['matching'],
            rating=validated_data['rating'],
            comment=validated_data.get('comment', ''),
            user=self.context['request'].user
        )
class ReviewStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['status']

    def validate_status(self, value):
        if value not in [ReviewStatus.ACCEPTED, ReviewStatus.REJECTED]:
            raise serializers.ValidationError("Only accept or reject operations are allowed.")
        return value

    def update(self, instance, validated_data):
        old_status = instance.status  
        new_status = validated_data.get('status', instance.status)

        instance.status = new_status
        instance.save()

        if old_status != ReviewStatus.ACCEPTED and new_status == ReviewStatus.ACCEPTED:
            NotificationService.send_review_notification(instance)

        return instance