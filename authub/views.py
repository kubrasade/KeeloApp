from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import logout
from .services import AuthService
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = AuthService.register_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            user_type=serializer.validated_data['user_type']
        )
        
        return Response(
            {"message": "Registration successful. Please verify your email address."},
            status=status.HTTP_201_CREATED
        )

class EmailVerificationView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        if AuthService.verify_email(uidb64, token):
            return Response(
                {"message": "Email verification successful."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Invalid or expired verification link."},
            status=status.HTTP_400_BAD_REQUEST
        )

class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = AuthService.login_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        return Response(result, status=status.HTTP_200_OK)

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"message": "Successfully logged out."},
            status=status.HTTP_200_OK
        )

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if AuthService.request_password_reset(serializer.validated_data['email']):
            return Response(
                {"message": "Password reset link has been sent to your email address."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "No registered user was found with this email address."},
            status=status.HTTP_400_BAD_REQUEST
        )

class PasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if AuthService.reset_password(
            uidb64,
            token,
            serializer.validated_data['new_password']
        ):
            return Response(
                {"message": "Your password has been successfully reset."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Invalid or expired password reset link."},
            status=status.HTTP_400_BAD_REQUEST
        )

class TokenRefreshView(TokenRefreshView):
    pass
