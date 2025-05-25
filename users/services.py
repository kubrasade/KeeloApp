from django.contrib.auth import get_user_model
from .models import DietitianProfile, ClientProfile, Specialization, HealthMetric
from .enums import HealthMetricType
from core.enums import UserType

User = get_user_model()

class UserService:
    @staticmethod
    def create_user(email, password, **extra_fields):
        user = User.objects.create_user(email=email, password=password, **extra_fields)
        return user

    @staticmethod
    def update_user(user, **data):
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

class DietitianProfileService:
    @staticmethod
    def create_profile(user, **validated_data):
        specializations = validated_data.pop("specializations", [])
        profile = DietitianProfile.objects.create(user=user, **validated_data)
        profile.specializations.set(specializations)
        return profile

    @staticmethod
    def update_profile(profile, **validated_data):
        specializations = validated_data.pop("specializations", None)
    
        for key, value in validated_data.items():
            setattr(profile, key, value)
    
        profile.save()
    
        if specializations is not None:
            profile.specializations.set(specializations)
    
        return profile

    @staticmethod
    def get_dietitian_profiles(user=None):
        if user and user.is_staff:
            return DietitianProfile.objects.all()
        return DietitianProfile.objects.filter(user=user)

class ClientProfileService:
    @staticmethod
    def create_profile(user, **data):
        profile = ClientProfile.objects.create(user=user, **data)
        return profile

    @staticmethod
    def update_profile(profile, **data):
        for key, value in data.items():
            setattr(profile, key, value)
        profile.save()
        return profile

    @staticmethod
    def get_client_profiles(user=None):
        if user and user.is_staff:
            return ClientProfile.objects.all()
        return ClientProfile.objects.filter(user=user)

class SpecializationService:
    @staticmethod
    def create_specialization(**data):
        specialization = Specialization.objects.create(**data)
        return specialization

    @staticmethod
    def update_specialization(specialization, **data):
        for key, value in data.items():
            setattr(specialization, key, value)
        specialization.save()
        return specialization

    @staticmethod
    def get_specializations():
        return Specialization.objects.all()

class HealthMetricService:
    @staticmethod
    def calculate_bmi(weight: float, height_cm: float) -> float:
        height_m = height_cm / 100
        if height_m > 0:
            return round(weight / (height_m ** 2), 2)
        return 0

    @staticmethod
    def create_metric(client, **data):
        if data.get('metric_type') == HealthMetricType.BMI:
            weight = data.get('weight')
            height = data.get('height')
            if weight is not None and height is not None:
                data['value'] = HealthMetricService.calculate_bmi(float(weight), float(height))
                data['unit'] = 'kg/m2'
                data.pop('weight', None)
                data.pop('height', None)
            else:
                raise ValueError('Current weight and height are required to calculate BMI.')
        metric = HealthMetric.objects.create(client=client, **data)
        return metric

    @staticmethod
    def update_metric(metric, **data):
        for key, value in data.items():
            setattr(metric, key, value)
        metric.save()
        return metric

    @staticmethod
    def get_metrics(user=None):
        if user and user.is_staff or user.user_type == UserType.DIETITIAN:
            return HealthMetric.objects.all()
        return HealthMetric.objects.filter(client=user) 