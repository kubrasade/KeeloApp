from rest_framework import serializers
from .models import Appointment
from users.models import DietitianProfile, User, ClientProfile

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

class AppointmentSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    dietitian = serializers.PrimaryKeyRelatedField(queryset=DietitianProfile.objects.all())
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    client_full_name = serializers.SerializerMethodField()
    dietitian_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'client_full_name', 'dietitian_full_name','id', 'client', 'dietitian', 'date', 'duration_minutes',
            'notes', 'status', 'created_at', 'updated_at', 'status_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_client_full_name(self, obj):
        return obj.client.user.get_full_name() if obj.client else ""

    def get_dietitian_full_name(self, obj):
        return obj.dietitian.user.get_full_name() if obj.dietitian else ""