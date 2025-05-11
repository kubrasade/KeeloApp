from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'dietitian', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('client__email', 'dietitian__user__email')