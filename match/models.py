from django.db import models
from core.models import BaseModel
from users.models import ClientProfile, Specialization
from django.contrib.auth import get_user_model

User = get_user_model()

class SpecializationChoice(BaseModel):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='specialization_choices')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='client_choices')

    class Meta:
        unique_together = ('client', 'specialization')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client.user.get_full_name()} - {self.specialization.name}"