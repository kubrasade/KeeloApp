from django.db import models
from core.models import BaseModel
from users.models import ClientProfile, Specialization, DietitianProfile
from django.contrib.auth import get_user_model
from core.enums import MatchingStatus, ReviewStatus
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class SpecializationChoice(BaseModel):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='specialization_choices')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='client_choices')

    class Meta:
        unique_together = ('client', 'specialization')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client.user.get_full_name()} - {self.specialization.name}"
    
class MatchModel(BaseModel):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='client_matchings')
    dietitian = models.ForeignKey(DietitianProfile, on_delete=models.CASCADE, related_name='dietitian_matchings')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='specialization_matchings')
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


class Review(BaseModel):
    matching = models.OneToOneField(MatchModel, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank= True, null= True)
    status = models.PositiveSmallIntegerField(choices= ReviewStatus.choices, default= ReviewStatus.PENDING)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.matching.dietitian.user.get_full_name()} by {self.matching.client.user.get_full_name()}" 




