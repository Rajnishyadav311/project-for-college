from django.contrib import admin
from .models import HealthMeasurement

@admin.register(HealthMeasurement)
class HealthMeasurementAdmin(admin.ModelAdmin):
    list_display = ('user', 'recorded_at', 'weight_kg', 'height_cm', 'bmi', 'bmi_category', 'systolic_bp', 'diastolic_bp', 'blood_glucose', 'heart_rate')
    list_filter = ('bmi_category', 'recorded_at')
    search_fields = ('user__username',)
