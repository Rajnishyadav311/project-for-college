import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from core.models import DoctorProfile
from .models import Appointment, DoctorReview
from .forms import AppointmentBookingForm, DoctorAppointmentUpdateForm, DoctorReviewForm, DoctorReplyForm

def find_doctors(request):
    query = request.GET.get('q', '').strip()
    specialty = request.GET.get('specialty', '').strip()
    city = request.GET.get('city', '').strip()

    doctors = DoctorProfile.objects.select_related('user').annotate(
        avg_rating=Avg('received_reviews__rating')
    ).all()

    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(clinic_name__icontains=query) |
            Q(specialization__icontains=query)
        )
    if specialty:
        doctors = doctors.filter(specialization=specialty)
    if city:
        doctors = doctors.filter(city__icontains=city)

    # Prepare map markers data for Leaflet
    doctors_map_data = []
    for doc in doctors:
        doctors_map_data.append({
            'id': doc.id,
            'name': f"Dr. {doc.user.get_full_name() or doc.user.username}",
            'specialty': doc.specialization,
            'clinic': doc.clinic_name,
            'address': doc.clinic_address,
            'city': doc.city,
            'fee': str(doc.consultation_fee),
            'lat': doc.latitude,
            'lng': doc.longitude,
            'url': f"/appointments/doctor/{doc.id}/"
        })

    specialties = [s[0] for s in DoctorProfile.SPECIALIZATIONS]

    return render(request, 'appointments/find_doctors.html', {
        'doctors': doctors,
        'specialties': specialties,
        'selected_specialty': specialty,
        'selected_city': city,
        'query': query,
        'map_data_json': json.dumps(doctors_map_data),
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(DoctorProfile.objects.select_related('user'), pk=pk)
    reviews = doctor.received_reviews.select_related('patient').all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating_display = round(avg_rating, 1) if avg_rating else 'New'

    return render(request, 'appointments/doctor_profile.html', {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': avg_rating_display,
        'review_count': reviews.count(),
    })


@login_required
def book_appointment(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)

    if request.user.is_doctor and request.user.doctor_profile == doctor:
        messages.warning(request, "Doctors cannot book appointments with themselves.")
        return redirect('appointments:find_doctors')

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = request.user
            appt.doctor = doctor
            appt.status = 'pending'
            appt.save()
            messages.success(request, f"Appointment request submitted with Dr. {doctor.user.get_full_name() or doctor.user.username}. Waiting for doctor confirmation.")
            return redirect('appointments:my_appointments')
    else:
        form = AppointmentBookingForm()

    return render(request, 'appointments/book.html', {
        'doctor': doctor,
        'form': form
    })


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).select_related('doctor', 'doctor__user')
    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})


@login_required
def doctor_manage_appointments(request):
    if not request.user.is_doctor or not hasattr(request.user, 'doctor_profile'):
        messages.error(request, "Access restricted to registered healthcare professionals.")
        return redirect('core:home')

    doctor = request.user.doctor_profile
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    return render(request, 'appointments/doctor_appointments.html', {
        'doctor': doctor,
        'appointments': appointments,
        'status_filter': status_filter
    })


@login_required
def update_appointment_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    # Check permission (must be the assigned doctor or admin)
    if not (request.user.is_doctor and request.user.doctor_profile == appointment.doctor) and not request.user.is_platform_admin:
        messages.error(request, "Access denied.")
        return redirect('appointments:my_appointments')

    if request.method == 'POST':
        form = DoctorAppointmentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Appointment #{appointment.id} updated to {appointment.get_status_display()}.")
            return redirect('appointments:doctor_manage')
    else:
        form = DoctorAppointmentUpdateForm(instance=appointment)

    return render(request, 'appointments/update_status.html', {
        'appointment': appointment,
        'form': form
    })


@login_required
def add_review(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)

    # Check if patient already reviewed this doctor
    existing = DoctorReview.objects.filter(patient=request.user, doctor=doctor).first()
    if existing:
        messages.info(request, "You have already reviewed this doctor.")
        return redirect('appointments:doctor_detail', pk=doctor.pk)

    if request.method == 'POST':
        form = DoctorReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.patient = request.user
            review.doctor = doctor
            review.save()
            messages.success(request, "Thank you for sharing your feedback!")
            return redirect('appointments:doctor_detail', pk=doctor.pk)
    else:
        form = DoctorReviewForm()

    return render(request, 'appointments/add_review.html', {
        'doctor': doctor,
        'form': form
    })


@login_required
def doctor_reply_review(request, pk):
    review = get_object_or_404(DoctorReview, pk=pk)
    if not (request.user.is_doctor and request.user.doctor_profile == review.doctor):
        messages.error(request, "Only the reviewed physician can post a response.")
        return redirect('appointments:find_doctors')

    if request.method == 'POST':
        form = DoctorReplyForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Professional response posted.")
            return redirect('appointments:doctor_detail', pk=review.doctor.pk)
    else:
        form = DoctorReplyForm(instance=review)

    return render(request, 'appointments/reply_review.html', {
        'review': review,
        'form': form
    })
