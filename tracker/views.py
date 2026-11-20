import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import HealthMeasurement
from .forms import HealthMeasurementForm

@login_required
def tracker_dashboard(request):
    measurements = HealthMeasurement.objects.filter(user=request.user).order_by('-recorded_at')
    latest = measurements.first()

    # Chronological series for Chart.js
    chronological = list(HealthMeasurement.objects.filter(user=request.user).order_by('recorded_at')[:30])

    dates = [m.recorded_at.strftime('%d-%b') for m in chronological]
    weights = [m.weight_kg for m in chronological]
    bmis = [m.bmi for m in chronological]
    systolics = [m.systolic_bp for m in chronological]
    diastolics = [m.diastolic_bp for m in chronological]
    glucoses = [m.blood_glucose for m in chronological]
    heart_rates = [m.heart_rate for m in chronological]

    chart_data = {
        'dates': dates,
        'weights': weights,
        'bmis': bmis,
        'systolics': systolics,
        'diastolics': diastolics,
        'glucoses': glucoses,
        'heart_rates': heart_rates,
    }

    return render(request, 'tracker/dashboard.html', {
        'measurements': measurements,
        'latest': latest,
        'chart_data_json': json.dumps(chart_data),
    })

@login_required
def add_measurement(request):
    if request.method == 'POST':
        form = HealthMeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.user = request.user
            measurement.save()
            messages.success(request, f"Health measurement recorded (BMI: {measurement.bmi} - {measurement.bmi_category}).")
            return redirect('tracker:dashboard')
    else:
        # Pre-fill height if existing
        prev = HealthMeasurement.objects.filter(user=request.user).first()
        initial = {'height_cm': prev.height_cm} if prev else {}
        form = HealthMeasurementForm(initial=initial)

    return render(request, 'tracker/form.html', {'form': form, 'title': 'Log Health Vitals'})

@login_required
def edit_measurement(request, pk):
    measurement = get_object_or_404(HealthMeasurement, pk=pk, user=request.user)
    if request.method == 'POST':
        form = HealthMeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Measurement entry updated.')
            return redirect('tracker:dashboard')
    else:
        form = HealthMeasurementForm(instance=measurement)

    return render(request, 'tracker/form.html', {'form': form, 'title': 'Edit Health Vitals', 'is_edit': True})

@login_required
def delete_measurement(request, pk):
    measurement = get_object_or_404(HealthMeasurement, pk=pk, user=request.user)
    if request.method == 'POST':
        measurement.delete()
        messages.success(request, 'Measurement deleted.')
        return redirect('tracker:dashboard')
    return render(request, 'tracker/delete_confirm.html', {'measurement': measurement})
