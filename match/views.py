from rest_framework import generics, status, exceptions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MatchModel, Review, SpecializationChoice
from .serializers import (
    MatchingSerializer,
    MatchingUpdateSerializer,
    ReviewSerializer,
    SpecializationChoiceSerializer,
    DietitianScoreSerializer,
    ReviewStatusUpdateSerializer
)
from .services import (
    MatchingService,
    ReviewService,
    SpecializationChoiceService,
    DietitianScoringService
)
from core.permissions import IsClient, IsAdmin
from users.models import Specialization, ClientProfile
from core.enums import UserType, ReviewStatus

class SpecializationChoiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = SpecializationChoiceSerializer

    def get_queryset(self):
        return SpecializationChoiceService.get_client_choices(self.request.user.client_profile)

    def perform_create(self, serializer):
        client = self.request.user.client_profile
        specialization = serializer.validated_data['specialization']
        choice = SpecializationChoiceService.create_choice(client, specialization)
        serializer.instance = choice


class DietitianListBySpecializationView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = DietitianScoreSerializer

    def get_queryset(self):
        specialization_id = self.kwargs.get('specialization_id')
        try:
            specialization = Specialization.objects.get(id=specialization_id)
            scored_dietitians = DietitianScoringService.get_dietitians_by_specialization(specialization)
            return [item['dietitian'] for item in scored_dietitians]
        except Specialization.DoesNotExist:
            return []


