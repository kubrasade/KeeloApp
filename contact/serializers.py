from rest_framework import serializers
from .models import ContactFormModel

class ContactFormModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormModel
        fields = ['id', 'name', 'surname', 'email', 'phone', 'message']