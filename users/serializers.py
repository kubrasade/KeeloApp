from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DietitianProfile, ClientProfile, Specialization, HealthMetric
from core.enums import UserType, Gender
from .enums import FitnessLevel, HealthMetricType

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(source='clientprofile.id', read_only=True) 

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name', 'user_type',
            'phone_number', 'client_id'
        ]
        read_only_fields = ['id', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'code', 'name', 'description']

class DietitianProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)
    specializations_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Specialization.objects.all(),
        source='specializations',  # `specializations` ile ilişkilendirilmiş alan
        write_only=True
    )

    class Meta:
        model = DietitianProfile
        fields = [
            'id', 'user', 'specializations', 'specializations_ids',  # `specializations_ids`'ı ekliyoruz
            'bio', 'education', 'experience_years', 'certificate_info',
            'consultation_fee', 'availability', 'rating', 'total_ratings',
            'website', 'social_links', 'profile_picture', 'gender', 'birth_date',
        ]
        read_only_fields = ['id', 'rating', 'total_ratings']

    def create(self, validated_data):
        specializations = validated_data.pop('specializations', [])
        instance = DietitianProfile.objects.create(**validated_data)
        instance.specializations.set(specializations)
        return instance

    def update(self, instance, validated_data):
        specializations = validated_data.pop('specializations', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if specializations is not None:
            instance.specializations.set(specializations)
        elif self.partial is False:  # PUT ise ve hiç gelmediyse, boşalt!
            instance.specializations.set([])
        return instance
    
class ClientProfileSerializer(serializers.ModelSerializer):
    dietitian = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type=UserType.DIETITIAN),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'dietitian', 'birth_place', 'profile_picture', 'gender', 'birth_date',
            'height', 'weight', 'target_weight', 'health_conditions', 'allergies',
            'medications', 'lifestyle', 'fitness_level', 'dietary_preferences'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        profile = super().create(validated_data)
        return profile

class HealthMetricSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type=UserType.CLIENT)
    )
    metric_type_display = serializers.SerializerMethodField()

    class Meta:
        model = HealthMetric
        fields = [
            'id', 'client', 'metric_type', 'metric_type_display',
            'value', 'unit', 'date_recorded', 'notes'
        ]
        read_only_fields = ['id']

    def get_metric_type_display(self, obj):
        return HealthMetricType(obj.metric_type).label 