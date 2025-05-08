from django.contrib.auth import get_user_model
from .models import DietitianProfile, ClientProfile, Specialization, HealthMetric

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
        # specializations'ı çıkarıyoruz
        specializations = validated_data.pop("specializations", None)
    
        # Diğer alanları güncelliyoruz
        for key, value in validated_data.items():
            setattr(profile, key, value)
    
        # Profilin kaydedilmesi
        profile.save()
    
        # Eğer specializations verisi varsa, set() ile ilişkiyi güncelliyoruz
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
    def create_metric(client, **data):
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
        if user and user.is_staff:
            return HealthMetric.objects.all()
        return HealthMetric.objects.filter(client=user) 