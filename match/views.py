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


class MatchingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MatchingSerializer

    def get_queryset(self):
        user_type = self.request.user.user_type

        if user_type == UserType.CLIENT:
            return MatchingService.get_client_matchings(self.request.user.client_profile)

        elif user_type == UserType.DIETITIAN:
            return MatchingService.get_dietitian_matchings(self.request.user.dietitian_profile)

        elif user_type == UserType.ADMIN:
            return MatchModel.objects.all()

        return MatchModel.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type not in [UserType.CLIENT, UserType.ADMIN]:
            raise exceptions.PermissionDenied("Only clients or admins can send matching requests.")

        if user.user_type == UserType.ADMIN:
            client_id = self.request.data.get('client_id')
            if not client_id:
                raise exceptions.ValidationError("Admin must provide client_id.")
            try:
                client = ClientProfile.objects.get(id=client_id)
            except ClientProfile.DoesNotExist:
                raise exceptions.ValidationError("Client not found.")
        else:
            client = user.client_profile

        dietitian = serializer.validated_data['dietitian']
        specialization = serializer.validated_data['specialization']

        matching = MatchingService.create_matching(client, dietitian, specialization)
        serializer.instance = matching

class MatchingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MatchModel.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchingSerializer
        return MatchingUpdateSerializer

    def perform_update(self, serializer):
        matching = self.get_object()
        new_status = serializer.validated_data['status']
        
        updated_matching = MatchingService.update_matching_status(
            matching=matching,
            status=new_status,
            user=self.request.user
        )
        serializer.instance = updated_matching


class ReviewListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user_type = self.request.user.user_type
        if user_type == UserType.CLIENT:
            return ReviewService.get_client_reviews(self.request.user.client_profile).filter(status=ReviewStatus.ACCEPTED)
        elif user_type == UserType.DIETITIAN:
            return ReviewService.get_dietitian_reviews(self.request.user.dietitian_profile).filter(status=ReviewStatus.ACCEPTED)
        elif user_type == UserType.ADMIN:
            return Review.objects.all()
        return Review.objects.none()

    def perform_create(self, serializer):
        matching = serializer.validated_data['matching']
        rating = serializer.validated_data['rating']
        comment = serializer.validated_data['comment']
        
        review = ReviewService.create_review(
            matching=matching,
            rating=rating,
            comment=comment,
            user=self.request.user
        )
        serializer.instance = review


