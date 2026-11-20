from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import DoctorProfile

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    TIME_SLOTS = [
        ('09:00 AM', '09:00 AM - 09:30 AM'),
        ('09:30 AM', '09:30 AM - 10:00 AM'),
        ('10:00 AM', '10:00 AM - 10:30 AM'),
        ('10:30 AM', '10:30 AM - 11:00 AM'),
        ('11:00 AM', '11:00 AM - 11:30 AM'),
        ('11:30 AM', '11:30 AM - 12:00 PM'),
        ('02:00 PM', '02:00 PM - 02:30 PM'),
        ('02:30 PM', '02:30 PM - 03:00 PM'),
        ('03:00 PM', '03:00 PM - 03:30 PM'),
        ('03:30 PM', '03:30 PM - 04:00 PM'),
        ('04:00 PM', '04:00 PM - 04:30 PM'),
        ('04:30 PM', '04:30 PM - 05:00 PM'),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    appointment_date = models.DateField(default=timezone.now)
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS, default='10:00 AM')
    symptoms_reason = models.TextField(help_text="Reason for consultation or description of symptoms")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    doctor_notes = models.TextField(blank=True, null=True, help_text="Doctor clinical observations or consultation summary")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', 'time_slot']

    def __str__(self):
        return f"Appt #{self.id}: {self.patient.username} with Dr. {self.doctor.user.last_name} ({self.appointment_date})"


class DoctorReview(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)], default=5)
    comment = models.TextField(help_text="Patient feedback regarding consultation and care")
    doctor_reply = models.TextField(blank=True, null=True, help_text="Response from the attending doctor")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.patient.username} for Dr. {self.doctor.user.username} ({self.rating}★)"
