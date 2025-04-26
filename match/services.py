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
