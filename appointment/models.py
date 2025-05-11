from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from users.models import DietitianProfile, ClientProfile
from core.models import BaseModel
from .enums import AppointmentStatus

User= get_user_model()

class Appointment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    dietitian = models.ForeignKey(
        DietitianProfile,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    notes = models.TextField(blank=True)
    status = models.PositiveSmallIntegerField(choices=AppointmentStatus.choices, default=AppointmentStatus.PENDING)


    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Appointment: {self.client.get_full_name()} with {self.dietitian.user.get_full_name()} on {self.date.strftime('%Y-%m-%d %H:%M')}"