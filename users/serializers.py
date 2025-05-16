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
        source='specializations',  
        write_only=True
    )

    class Meta:
        model = DietitianProfile
        fields = [
            'id', 'user', 'specializations', 'specializations_ids', 
            'bio', 'education', 'experience_years', 'certificate_info',
            'consultation_fee', 'availability', 'rating', 'total_ratings',
            'website', 'social_links', 'profile_picture', 'gender', 'birth_date', 'city', 'license_number'
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
        elif self.partial is False:  
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
    client = serializers.PrimaryKeyRelatedField(read_only=True)
    metric_type_display = serializers.SerializerMethodField()
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, write_only=True)
    height = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, write_only=True)
    unit = serializers.CharField(max_length=20, required=False)
    value = serializers.CharField(max_length=20, required=False)

    class Meta:
        model = HealthMetric
        fields = [
            'id', 'client', 'metric_type', 'metric_type_display',
            'value', 'unit', 'date_recorded', 'notes', 'weight', 'height'
        ]
        read_only_fields = ['id', 'client']

    def get_metric_type_display(self, obj):
        return HealthMetricType(obj.metric_type).label 

    def validate(self, data):
        metric_type = data.get('metric_type')
        if int(metric_type) == HealthMetricType.BMI:
            if not data.get('weight') or not data.get('height'):
                raise serializers.ValidationError({
                    "weight": "Weight is required for BMI.",
                    "height": "Height is required for BMI."
                })
        else:
            if not data.get('value'):
                raise serializers.ValidationError({"value": "This field is required."})
            if not data.get('unit'):
                raise serializers.ValidationError({"unit": "This field is required."})
        return data

    def create(self, validated_data):
        metric_type = validated_data.get('metric_type')
        if int(metric_type) == HealthMetricType.BMI:
            weight = validated_data.pop('weight', None)
            height = validated_data.pop('height', None)
            if weight is not None and height is not None:
                height_m = float(height) / 100
                bmi = round(float(weight) / (height_m ** 2), 2) if height_m > 0 else 0
                validated_data['value'] = bmi
                validated_data['unit'] = 'kg/m2'
            else:
                raise serializers.ValidationError({
                    "weight": "Weight is required for BMI.",
                    "height": "Height is required for BMI."
                })
        return super().create(validated_data)