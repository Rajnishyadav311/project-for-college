from appointments.models import Appointment

def global_context(request):
    context = {
        'APP_NAME': 'MediPredict AI',
        'APP_TAGLINE': 'Intelligent Healthcare & Predictive Diagnostic Platform',
    }
    if request.user.is_authenticated:
        context['is_patient'] = request.user.is_patient
        context['is_doctor'] = request.user.is_doctor
        context['is_platform_admin'] = request.user.is_platform_admin

        # Unread/pending appointments count
        try:
            if request.user.is_doctor and hasattr(request.user, 'doctor_profile'):
                context['pending_appointments_count'] = Appointment.objects.filter(
                    doctor=request.user.doctor_profile, status='pending'
                ).count()
            elif request.user.is_patient:
                context['upcoming_appointments_count'] = Appointment.objects.filter(
                    patient=request.user, status__in=['pending', 'confirmed']
                ).count()
        except Exception:
            pass

    return context
