from .models import MatchModel, Review, SpecializationChoice
from users.models import  DietitianProfile
from core.enums import MatchingStatus
from django.utils import timezone
from rest_framework import exceptions
from django.db.models import Avg, Count

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
        rating_weight = 0.4
        experience_weight = 0.3
        review_count_weight = 0.3

        avg_rating = Review.objects.filter(matching__dietitian=dietitian).aggregate(Avg('rating'))['rating__avg'] or 0

        experience_years = dietitian.experience_years or 0 

        review_count = Review.objects.filter(matching__dietitian=dietitian).count()

        max_experience = 30  
        max_reviews = 100    

        normalized_experience = min(experience_years / max_experience, 1)
        normalized_reviews = min(review_count / max_reviews, 1)

        return {
            'average_rating': avg_rating,
            'experience_years': experience_years,
            'review_count': review_count,
            'total_score': (
                (avg_rating / 5) * rating_weight +
                normalized_experience * experience_weight +
                normalized_reviews * review_count_weight
            ) * 100
        }

    @staticmethod
    def get_dietitians_by_specialization(specialization):
        dietitians = DietitianProfile.objects.filter(specializations=specialization)
        scored_dietitians = []
        
        for dietitian in dietitians:
            score = DietitianScoringService.calculate_dietitian_score(dietitian)
            scored_dietitians.append({
                'dietitian': dietitian,
                'score': score
            })
        
        return sorted(scored_dietitians, key=lambda x: x['score']['total_score'], reverse=True)

