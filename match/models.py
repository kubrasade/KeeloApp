from django.db import models
from core.models import BaseModel
from users.models import ClientProfile, Specialization, DietitianProfile
from django.contrib.auth import get_user_model
from core.enums import MatchingStatus

User = get_user_model()

class SpecializationChoice(BaseModel):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='specialization_choices')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='client_choices')

    class Meta:
        unique_together = ('client', 'specialization')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client.user.get_full_name()} - {self.specialization.name}"
    
class Matching(BaseModel):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='matchings')
    dietitian = models.ForeignKey(DietitianProfile, on_delete=models.CASCADE, related_name='matchings')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='matchings')
    status = models.PositiveSmallIntegerField(
        choices=MatchingStatus.choices,
        default=MatchingStatus.PENDING
    )
    matched_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('client', 'dietitian', 'specialization')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client.user.get_full_name()} - {self.dietitian.user.get_full_name()} ({self.specialization.name})"
