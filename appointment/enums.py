from django.db import models 

class AppointmentStatus(models.IntegerChoices):
    PENDING = 1, 'Pending'
    CONFIRMED = 2, 'Confirmed'
    COMPLETED = 3, 'Completed',
    CANCELLED = 4, 'Cancelled'

