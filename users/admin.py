from django.contrib import admin
from .models import User, Specialization, DietitianProfile, ClientProfile, HealthMetric

admin.site.register(User)
admin.site.register(Specialization)
admin.site.register(DietitianProfile)
admin.site.register(ClientProfile)
admin.site.register(HealthMetric)