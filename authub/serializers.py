from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from core.enums import UserType
from users.models import ClientProfile, DietitianProfile

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    license_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name','user_type', 'license_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'user_type': {'required':True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password do not match."})
        if attrs['user_type'] == UserType.DIETITIAN.value and not attrs.get('license_number'):
            raise serializers.ValidationError({"license_number": "Licence number is required for dietitians."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        license_number = validated_data.pop('license_number', None)
        user = User.objects.create_user(**validated_data)
        if user.user_type == UserType.DIETITIAN.value:
            DietitianProfile.objects.create(user=user, license_number=license_number)
        elif user.user_type == UserType.CLIENT.value:
            ClientProfile.objects.create(user=user)
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs 