from .models import MatchModel, Review, SpecializationChoice
from users.models import  DietitianProfile
from core.enums import MatchingStatus
from django.utils import timezone
from rest_framework import exceptions
from django.db.models import Avg, Count
from django.conf import settings
from django.core.cache import cache
from notifications.services import NotificationService  

class SpecializationChoiceService:
    @staticmethod
    def create_choice(client, specialization):
        if SpecializationChoice.objects.filter(client=client, specialization=specialization).exists():
            raise exceptions.ValidationError("You have already chosen this specialization.")
        
        return SpecializationChoice.objects.create(
            client=client,
            specialization=specialization
        )

    @staticmethod
    def get_client_choices(client):
        return SpecializationChoice.objects.filter(client=client)


class DietitianScoringService:
    @staticmethod

    def calculate_dietitian_score(dietitian):
        cache_key = f'dietitian_score_{dietitian.id}'
        cached_score = cache.get(cache_key)
        if cached_score:
            return cached_score

        rating_weight = settings.RATING_WEIGHT
        experience_weight = settings.EXPERIENCE_WEIGHT
        review_count_weight = settings.REVIEW_COUNT_WEIGHT

        avg_rating = Review.objects.filter(matching__dietitian=dietitian).aggregate(Avg('rating'))['rating__avg'] or 0
        experience_years = dietitian.experience_years or 0
        review_count = Review.objects.filter(matching__dietitian=dietitian).count()

        normalized_experience = min(experience_years / 30, 1)  
        normalized_reviews = min(review_count / 100, 1)        

        score = {
            'average_rating': avg_rating,
            'experience_years': experience_years,
            'review_count': review_count,
            'total_score': (
                (avg_rating / 5) * rating_weight +
                normalized_experience * experience_weight +
                normalized_reviews * review_count_weight
            ) * 100
        }

        cache.set(cache_key, score, timeout=settings.CACHE_TTL)
        return score

    @staticmethod
    def get_dietitians_by_specialization_queryset(specialization):
        dietitians = DietitianProfile.objects.filter(specializations=specialization)
        scored_dietitians = []
        
        for dietitian in dietitians:
            score = DietitianScoringService.calculate_dietitian_score(dietitian)
            scored_dietitians.append({
                'dietitian': dietitian,
                'score': score
            })
        
        return sorted(scored_dietitians, key=lambda x: x['score']['total_score'], reverse=True)

class MatchingService:
    @staticmethod
    def create_matching(client, dietitian, specialization):
        if not dietitian.specializations.filter(id=specialization.id).exists():
            raise exceptions.ValidationError("This dietitian is not in your chosen specialty.")
        
        if MatchModel.objects.filter(
            client=client,
            dietitian=dietitian,
            specialization=specialization
        ).exists():
            raise exceptions.ValidationError("This match already exists.")
        
        return MatchModel.objects.create(
            client=client,
            dietitian=dietitian,
            specialization=specialization,
            status=MatchingStatus.PENDING
        )

    @staticmethod
    def update_matching_status(matching, status, user):
        if status not in [MatchingStatus.ACCEPTED, MatchingStatus.REJECTED, MatchingStatus.ENDED]:
            raise exceptions.ValidationError("Invalid status.")
        
        old_status = matching.status

        if status == MatchingStatus.ACCEPTED and matching.status == MatchingStatus.PENDING:
            if user != matching.dietitian.user and not user.is_staff:
                raise exceptions.PermissionDenied("You are not authorized to perform this operation.")
            matching.matched_at = timezone.now()
        
        elif status == MatchingStatus.ENDED:
            if user != matching.client.user and user != matching.dietitian.user and not user.is_staff:
                raise exceptions.PermissionDenied("You are not authorized to perform this operation.")
            matching.ended_at = timezone.now()
        
        matching.status = status
        matching.save()

        NotificationService.send_matching_status_notification(matching, old_status, status)
        
        return matching

    @staticmethod
    def get_client_matchings(client):
        return MatchModel.objects.filter(client=client)

    @staticmethod
    def get_dietitian_matchings(dietitian):
        return  MatchModel.objects.filter(dietitian=dietitian)

class ReviewService:
    @staticmethod
    def create_review(matching, rating, comment, user):
        if matching.client.user != user:
            raise exceptions.PermissionDenied("You can only comment to your own dietitian.")
        
        if matching.status != MatchingStatus.ACCEPTED:
            raise exceptions.ValidationError("You can only comment on active matches.")
        
        if Review.objects.filter(matching=matching).exists():
            raise exceptions.ValidationError("You have already commented on this dietitian.")
        
        return Review.objects.create(
            matching=matching,
            rating=rating,
            comment=comment
        )
        

    @staticmethod
    def get_dietitian_reviews(dietitian):
        return Review.objects.filter(matching__dietitian=dietitian)

    @staticmethod
    def get_client_reviews(client):
        return Review.objects.filter(matching__client=client) 
