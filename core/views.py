import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from .models import CustomUser, PatientProfile, DoctorProfile
from .forms import (
    PatientRegistrationForm, DoctorRegistrationForm, UserLoginForm,
    PatientProfileForm, DoctorProfileForm
)
from predictions.models import PredictionRecord
from reports.models import MedicalReport
from tracker.models import HealthMeasurement
from appointments.models import Appointment, DoctorReview

def home(request):
    """
    Landing Page for MediPredict AI.
    Features Hero, Introduction, 3 Disease Modules, Report Analyzer Preview,
    Doctor Finder Preview, How It Works, Healthcare Benefits, FAQs, and Footer.
    """
    total_doctors = DoctorProfile.objects.filter(is_verified=True).count()
    return render(request, 'core/home.html', {
        'total_doctors': total_doctors,
    })


def register_patient(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MediPredict AI, {user.first_name or user.username}! Your patient account is ready.")
            return redirect('core:patient_dashboard')
    else:
        form = PatientRegistrationForm()

    return render(request, 'core/register_patient.html', {'form': form})


def register_doctor(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Doctor profile submitted successfully for Dr. {user.get_full_name() or user.username}. Our admin team will verify your credentials.")
            return redirect('core:doctor_dashboard')
    else:
        form = DoctorRegistrationForm()

    return render(request, 'core/register_doctor.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('core:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'core/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('core:home')


@login_required
def dashboard_redirect(request):
    if request.user.is_platform_admin:
        return redirect('core:admin_dashboard')
    elif request.user.is_doctor:
        return redirect('core:doctor_dashboard')
    else:
        return redirect('core:patient_dashboard')


@login_required
def patient_dashboard(request):
    user = request.user
    reports = MedicalReport.objects.filter(user=user)[:5]
    total_reports = MedicalReport.objects.filter(user=user).count()

    predictions = PredictionRecord.objects.filter(user=user)[:5]
    total_predictions = PredictionRecord.objects.filter(user=user).count()

    appointments = Appointment.objects.filter(patient=user, status__in=['pending', 'confirmed'])[:3]
    total_appointments = Appointment.objects.filter(patient=user).count()

    latest_measurement = HealthMeasurement.objects.filter(user=user).first()

    # Trend charts data for quick health metrics
    recent_vitals = list(HealthMeasurement.objects.filter(user=user).order_by('recorded_at')[:10])
    vitals_chart = {
        'dates': [v.recorded_at.strftime('%d %b') for v in recent_vitals],
        'weights': [v.weight_kg for v in recent_vitals],
        'bmis': [v.bmi for v in recent_vitals],
        'glucose': [v.blood_glucose for v in recent_vitals if v.blood_glucose],
    }

    return render(request, 'core/patient_dashboard.html', {
        'total_reports': total_reports,
        'total_predictions': total_predictions,
        'total_appointments': total_appointments,
        'reports': reports,
        'predictions': predictions,
        'appointments': appointments,
        'latest_vitals': latest_measurement,
        'vitals_chart_json': json.dumps(vitals_chart),
    })


@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor or not hasattr(request.user, 'doctor_profile'):
        messages.error(request, "Doctor credentials required.")
        return redirect('core:home')

    doctor = request.user.doctor_profile
    pending_appts = Appointment.objects.filter(doctor=doctor, status='pending')
    confirmed_appts = Appointment.objects.filter(doctor=doctor, status='confirmed')
    completed_appts = Appointment.objects.filter(doctor=doctor, status='completed')
    recent_reviews = doctor.received_reviews.select_related('patient')[:5]

    avg_rating = doctor.received_reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'core/doctor_dashboard.html', {
        'doctor': doctor,
        'pending_appts': pending_appts,
        'confirmed_appts': confirmed_appts,
        'completed_appts': completed_appts,
        'recent_reviews': recent_reviews,
        'avg_rating': round(avg_rating, 1) if avg_rating else 'N/A',
        'total_patients': completed_appts.values('patient').distinct().count(),
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_platform_admin:
        messages.error(request, "Admin access required.")
        return redirect('core:home')

    total_patients = CustomUser.objects.filter(role='PATIENT').count()
    doctors = DoctorProfile.objects.select_related('user').all()
    total_doctors = doctors.count()
    verified_doctors = doctors.filter(is_verified=True).count()
    pending_doctors = doctors.filter(is_verified=False).count()

    total_predictions = PredictionRecord.objects.count()
    total_reports = MedicalReport.objects.count()
    total_appointments = Appointment.objects.count()

    predictions_by_type = PredictionRecord.objects.values('disease_type').annotate(count=Count('id'))

    return render(request, 'core/admin_dashboard.html', {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'verified_doctors': verified_doctors,
        'pending_doctors': pending_doctors,
        'total_predictions': total_predictions,
        'total_reports': total_reports,
        'total_appointments': total_appointments,
        'doctors': doctors,
        'predictions_by_type': predictions_by_type,
    })


@login_required
def admin_verify_doctor(request, pk):
    if not request.user.is_platform_admin:
        messages.error(request, "Permission denied.")
        return redirect('core:home')

    doctor = get_object_or_404(DoctorProfile, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            doctor.is_verified = True
            messages.success(request, f"Dr. {doctor.user.get_full_name()} verified successfully.")
        elif action == 'revoke':
            doctor.is_verified = False
            messages.info(request, f"Verification revoked for Dr. {doctor.user.get_full_name()}.")
        doctor.save()
    return redirect('core:admin_dashboard')


@login_required
def profile_view(request):
    user = request.user
    patient_form = None
    doctor_form = None

    if user.is_patient and hasattr(user, 'patient_profile'):
        if request.method == 'POST':
            patient_form = PatientProfileForm(request.POST, instance=user.patient_profile)
            if patient_form.is_valid():
                patient_form.save()
                messages.success(request, "Patient health profile updated.")
                return redirect('core:profile')
        else:
            patient_form = PatientProfileForm(instance=user.patient_profile)

    elif user.is_doctor and hasattr(user, 'doctor_profile'):
        if request.method == 'POST':
            doctor_form = DoctorProfileForm(request.POST, instance=user.doctor_profile)
            if doctor_form.is_valid():
                doctor_form.save()
                messages.success(request, "Doctor professional profile updated.")
                return redirect('core:profile')
        else:
            doctor_form = DoctorProfileForm(instance=user.doctor_profile)

    return render(request, 'core/profile.html', {
        'user': user,
        'patient_form': patient_form,
        'doctor_form': doctor_form,
    })
