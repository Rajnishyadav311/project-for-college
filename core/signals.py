from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, PatientProfile, DoctorProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'PATIENT':
            PatientProfile.objects.get_or_create(user=instance)
        elif instance.role == 'DOCTOR':
            DoctorProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'qualification': 'MBBS',
                    'specialization': 'General Physician',
                    'license_number': f"REG-{instance.id:05d}",
                    'clinic_name': 'MediPredict Partner Clinic',
                    'clinic_address': 'Connaught Place',
                    'city': 'New Delhi',
                    'latitude': 28.6139 + (instance.id * 0.005),
                    'longitude': 77.2090 + (instance.id * 0.005),
                    'consultation_fee': 600.00,
                    'is_verified': True if instance.is_superuser else False,
                }
            )
