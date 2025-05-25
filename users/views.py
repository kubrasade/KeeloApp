from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .models import DietitianProfile, ClientProfile, Specialization, HealthMetric
from .serializers import (
    UserSerializer, DietitianProfileSerializer,
    ClientProfileSerializer, SpecializationSerializer,
    HealthMetricSerializer
)
from .services import (
    UserService, DietitianProfileService,
    ClientProfileService, SpecializationService,
    HealthMetricService
)
from core.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, IsProfileOwnerOrAdmin

User = get_user_model()

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        data = serializer.validated_data.copy() 
        email = data.pop('email')
        password = data.pop('password', None)

        user = UserService.create_user(
            email=email,
            password=password,
            **data
        )
        serializer.instance = user

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_update(self, serializer):
        data = serializer.validated_data
        password = data.pop('password', None)
        user = serializer.instance
        if password:
            user.set_password(password)
        UserService.update_user(user, **data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

class DietitianProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = DietitianProfileSerializer
    permission_classes = [IsProfileOwnerOrAdmin]

    def get_queryset(self):
        return DietitianProfileService.get_dietitian_profiles(self.request.user)

    def perform_create(self, serializer):
        profile = DietitianProfileService.create_profile(
            user=self.request.user,
            **serializer.validated_data
        )
        serializer.instance = profile

class DietitianProfileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DietitianProfile.objects.all()
    serializer_class = DietitianProfileSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_update(self, serializer):
        DietitianProfileService.update_profile(
            serializer.instance,
            **serializer.validated_data
        )

class ClientProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ClientProfileService.get_client_profiles(self.request.user)

    def perform_create(self, serializer):
        profile = ClientProfileService.create_profile(
            user=self.request.user,
            **serializer.validated_data
        )
        serializer.instance = profile

class ClientProfileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_update(self, serializer):
        ClientProfileService.update_profile(
            serializer.instance,
            **serializer.validated_data
        )

class SpecializationListCreateView(generics.ListCreateAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        specialization = SpecializationService.create_specialization(
            **serializer.validated_data
        )
        serializer.instance = specialization

class SpecializationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_update(self, serializer):
        SpecializationService.update_specialization(
            serializer.instance,
            **serializer.validated_data
        )

class HealthMetricListCreateView(generics.ListCreateAPIView):
    serializer_class = HealthMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = HealthMetricService.get_metrics(self.request.user)
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

    def perform_create(self, serializer):
        validated_data = serializer.validated_data.copy()
        validated_data.pop('client', None)  
        
        metric = HealthMetricService.create_metric(
            client=self.request.user, 
            **validated_data
        )
        serializer.instance = metric

class HealthMetricRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HealthMetric.objects.all()
    serializer_class = HealthMetricSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_update(self, serializer):
        HealthMetricService.update_metric(
            serializer.instance,
            **serializer.validated_data
        )
