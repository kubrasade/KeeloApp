from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from users.models import ClientProfile, DietitianProfile
from core.enums import UserType
from .tasks import send_verification_email, send_password_reset_email

User = get_user_model()

class AuthService:
    @staticmethod
    def register_user(email, password, first_name, last_name, user_type):
        if User.objects.filter(email=email).exists():
            raise exceptions.ValidationError("This email address is already in use.")
        
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            is_active=False
        )

        if user.user_type == UserType.CLIENT.value:
            ClientProfile.objects.create(user=user)
        elif user.user_type == UserType.DIETITIAN.value:
            DietitianProfile.objects.create(user=user)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        send_verification_email.delay(
            email=email,
            uid=uid,
            token=token,
            first_name=first_name
        )

        return user

    @staticmethod
    def verify_email(uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return True
        return False

    @staticmethod
    def login_user(email, password):
        user = User.objects.filter(email=email).first()
        
        if not user or not user.check_password(password):
            raise exceptions.AuthenticationFailed('Email or password wrong.')
        
        if not user.is_active:
            raise exceptions.AuthenticationFailed('Your account is not active. Please verify your email.')
        
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


    @staticmethod
    def request_password_reset(email):
        user = User.objects.filter(email=email).first()
        if not user:
            return False

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        send_password_reset_email.delay(
            email=email,
            uid=uid,
            token=token,
            first_name=user.first_name
        )

        return True

    @staticmethod
    def reset_password(uidb64, token, new_password):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return True
        return False 