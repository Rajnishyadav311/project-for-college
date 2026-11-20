from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PredictionRecord
from .forms import DiabetesPredictionForm, HeartPredictionForm, KidneyPredictionForm
from .ml_engine import predict_disease_risk

def predict_home(request):
    return render(request, 'predictions/predict_home.html')

@login_required
def predict_diabetes(request):
    if request.method == 'POST':
        form = DiabetesPredictionForm(request.POST)
        if form.is_valid():
            inputs = form.cleaned_data
            result = predict_disease_risk('diabetes', inputs)

            record = PredictionRecord.objects.create(
                user=request.user,
                disease_type='diabetes',
                input_features=inputs,
                risk_score=result['risk_score'],
                risk_level=result['risk_level'],
                risk_label=result['risk_label'],
                feature_contributions=result['all_contributors'],
                model_version=result['model_version']
            )
            messages.success(request, 'Diabetes risk assessment computed successfully.')
            return redirect('predictions:result', pk=record.pk)
    else:
        # Pre-fill with user's profile or tracker measurements if available
        initial = {}
        if hasattr(request.user, 'tracker_measurements') and request.user.tracker_measurements.exists():
            latest = request.user.tracker_measurements.first()
            if latest.bmi: initial['bmi'] = latest.bmi
            if latest.blood_glucose: initial['glucose'] = latest.blood_glucose
            if latest.diastolic_bp: initial['blood_pressure'] = latest.diastolic_bp
        form = DiabetesPredictionForm(initial=initial)

    return render(request, 'predictions/predict_diabetes.html', {'form': form})

@login_required
def predict_heart(request):
    if request.method == 'POST':
        form = HeartPredictionForm(request.POST)
        if form.is_valid():
            inputs = form.cleaned_data
            result = predict_disease_risk('heart', inputs)

            record = PredictionRecord.objects.create(
                user=request.user,
                disease_type='heart',
                input_features=inputs,
                risk_score=result['risk_score'],
                risk_level=result['risk_level'],
                risk_label=result['risk_label'],
                feature_contributions=result['all_contributors'],
                model_version=result['model_version']
            )
            messages.success(request, 'Cardiovascular risk assessment computed successfully.')
            return redirect('predictions:result', pk=record.pk)
    else:
        initial = {}
        if hasattr(request.user, 'tracker_measurements') and request.user.tracker_measurements.exists():
            latest = request.user.tracker_measurements.first()
            if latest.systolic_bp: initial['trestbps'] = latest.systolic_bp
            if latest.heart_rate: initial['thalach'] = latest.heart_rate
        form = HeartPredictionForm(initial=initial)

    return render(request, 'predictions/predict_heart.html', {'form': form})

@login_required
def predict_kidney(request):
    if request.method == 'POST':
        form = KidneyPredictionForm(request.POST)
        if form.is_valid():
            inputs = form.cleaned_data
            result = predict_disease_risk('kidney', inputs)

            record = PredictionRecord.objects.create(
                user=request.user,
                disease_type='kidney',
                input_features=inputs,
                risk_score=result['risk_score'],
                risk_level=result['risk_level'],
                risk_label=result['risk_label'],
                feature_contributions=result['all_contributors'],
                model_version=result['model_version']
            )
            messages.success(request, 'Kidney disease risk assessment computed successfully.')
            return redirect('predictions:result', pk=record.pk)
    else:
        form = KidneyPredictionForm()

    return render(request, 'predictions/predict_kidney.html', {'form': form})

@login_required
def predict_result(request, pk):
    record = get_object_or_404(PredictionRecord, pk=pk)
    if record.user != request.user and not request.user.is_doctor and not request.user.is_platform_admin:
        messages.error(request, 'Access denied.')
        return redirect('predictions:history')

    return render(request, 'predictions/predict_result.html', {'record': record})

@login_required
def prediction_history(request):
    records = PredictionRecord.objects.filter(user=request.user)
    return render(request, 'predictions/history.html', {'records': records})
