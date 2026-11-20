from django.contrib import admin
from .models import Appointment, DoctorReview

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_date', 'time_slot', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__username', 'doctor__user__username')

@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'rating', 'created_at')
    list_filter = ('rating',)
