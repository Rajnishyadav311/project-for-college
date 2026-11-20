from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Administrator'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='PATIENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=15,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True, null=True
    )
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_patient(self):
        return self.role == 'PATIENT'

    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'

    @property
    def is_platform_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    def __str__(self):
        full = self.get_full_name()
        return full if full else self.username


class PatientProfile(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True, help_text="Known drug or food allergies")
    chronic_conditions = models.TextField(blank=True, null=True, help_text="e.g. Hypertension, Type 2 Diabetes")
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default='New Delhi')

    def __str__(self):
        return f"Patient: {self.user.username}"


class DoctorProfile(models.Model):
    SPECIALIZATIONS = [
        ('General Physician', 'General Physician'),
        ('Cardiologist', 'Cardiologist (Heart Specialist)'),
        ('Diabetologist / Endocrinologist', 'Diabetologist / Endocrinologist'),
        ('Nephrologist', 'Nephrologist (Kidney Specialist)'),
        ('Pathologist', 'Pathologist (Lab Medicine)'),
        ('Pulmonologist', 'Pulmonologist (Chest & Lungs)'),
        ('Neurologist', 'Neurologist'),
        ('Pediatrician', 'Pediatrician'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    qualification = models.CharField(max_length=150, help_text="e.g. MBBS, MD, DM (Cardiology)")
    specialization = models.CharField(max_length=60, choices=SPECIALIZATIONS, default='General Physician')
    license_number = models.CharField(max_length=50, unique=True, help_text="Medical Council Registration No.")
    clinic_name = models.CharField(max_length=150, default="City Health Clinic")
    clinic_address = models.TextField(default="Connaught Place, Central Delhi")
    city = models.CharField(max_length=100, default="New Delhi")
    latitude = models.FloatField(default=28.6139, help_text="GPS Latitude for map integration")
    longitude = models.FloatField(default=77.2090, help_text="GPS Longitude for map integration")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    experience_years = models.PositiveIntegerField(default=5)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text="Verified by MediPredict AI Admin")
    available_days = models.CharField(max_length=100, default="Mon, Tue, Wed, Thu, Fri, Sat")
    available_time_start = models.TimeField(default="09:00:00")
    available_time_end = models.TimeField(default="17:00:00")

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"
