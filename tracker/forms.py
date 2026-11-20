from django import forms
from .models import HealthMeasurement

class HealthMeasurementForm(forms.ModelForm):
    class Meta:
        model = HealthMeasurement
        fields = [
            'recorded_at', 'weight_kg', 'height_cm',
            'systolic_bp', 'diastolic_bp', 'blood_glucose', 'heart_rate', 'notes'
        ]
        widgets = {
            'recorded_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 72.5'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'e.g. 174.0'}),
            'systolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 120'}),
            'diastolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 80'}),
            'blood_glucose': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'placeholder': 'e.g. 98'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 72'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Morning fasting, post workout...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get('weight_kg')
        height = cleaned_data.get('height_cm')

        if weight is not None and weight <= 0:
            self.add_error('weight_kg', 'Weight must be a positive number.')
        if height is not None and (height < 30 or height > 280):
            self.add_error('height_cm', 'Please enter a valid height between 30 and 280 cm.')

        systolic = cleaned_data.get('systolic_bp')
        diastolic = cleaned_data.get('diastolic_bp')
        if systolic and diastolic and systolic <= diastolic:
            self.add_error('systolic_bp', 'Systolic blood pressure is typically higher than diastolic blood pressure.')

        return cleaned_data
