from django import forms

class DiabetesPredictionForm(forms.Form):
    glucose = forms.FloatField(
        label='Fasting Blood Glucose (mg/dL)',
        min_value=40.0, max_value=400.0, initial=105.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        help_text='Normal: 70-99 mg/dL, Prediabetes: 100-125 mg/dL, Diabetic: ≥126 mg/dL'
    )
    bmi = forms.FloatField(
        label='Body Mass Index (BMI in kg/m²)',
        min_value=12.0, max_value=70.0, initial=26.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text='Normal: 18.5-24.9, Overweight: 25.0-29.9, Obese: ≥30.0'
    )
    age = forms.IntegerField(
        label='Age (Years)',
        min_value=1, max_value=115, initial=45,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    blood_pressure = forms.FloatField(
        label='Diastolic Blood Pressure (mm Hg)',
        min_value=40.0, max_value=160.0, initial=78.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        help_text='Normal: <80 mm Hg'
    )
    insulin = forms.FloatField(
        label='Fasting Serum Insulin (µU/mL)',
        min_value=2.0, max_value=800.0, initial=85.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        help_text='Normal fasting range: 2.6 - 24.9 µU/mL'
    )
    pregnancies = forms.IntegerField(
        label='Number of Pregnancies',
        min_value=0, max_value=20, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Enter 0 for male patients or if nulliparous'
    )
    pedigree = forms.FloatField(
        label='Diabetes Pedigree Function Score',
        min_value=0.05, max_value=2.5, initial=0.45,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text='Calculated genetic clustering score (Average: 0.47)'
    )
    skin_thickness = forms.FloatField(
        label='Triceps Skinfold Thickness (mm)',
        min_value=5.0, max_value=100.0, initial=23.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        help_text='Average healthy range: 15-25 mm'
    )


class HeartPredictionForm(forms.Form):
    age = forms.IntegerField(
        label='Age (Years)',
        min_value=18, max_value=110, initial=54,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    sex = forms.ChoiceField(
        label='Biological Sex',
        choices=[(1, 'Male'), (0, 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cp = forms.ChoiceField(
        label='Chest Pain Symptoms',
        choices=[
            (0, 'Asymptomatic / No Chest Pain'),
            (1, 'Atypical Angina (Mild / Exertional discomfort)'),
            (2, 'Non-Anginal Discomfort'),
            (3, 'Typical Angina (Crushing / Retrosternal pressure)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    trestbps = forms.FloatField(
        label='Resting Blood Pressure (mm Hg)',
        min_value=80.0, max_value=240.0, initial=130.0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Optimal: <120 mm Hg'
    )
    chol = forms.FloatField(
        label='Total Serum Cholesterol (mg/dL)',
        min_value=100.0, max_value=600.0, initial=220.0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Desirable: <200 mg/dL, Borderline: 200-239, High: ≥240'
    )
    thalach = forms.FloatField(
        label='Maximum Achieved Heart Rate (bpm)',
        min_value=60.0, max_value=220.0, initial=148.0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Age-predicted maximum is roughly 220 minus age'
    )
    exang = forms.ChoiceField(
        label='Exercise Induced Angina',
        choices=[(0, 'No Angina during Exercise'), (1, 'Yes - Experiences Angina during Exercise')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    oldpeak = forms.FloatField(
        label='ST Depression (Oldpeak in mm)',
        min_value=0.0, max_value=7.0, initial=0.8,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text='Exercise relative to rest on ECG (Normal: 0.0 mm)'
    )
    slope = forms.ChoiceField(
        label='Slope of Peak Exercise ST Segment',
        choices=[
            (0, 'Upsloping (Normal cardiac response)'),
            (1, 'Flat (Borderline ischemic risk)'),
            (2, 'Downsloping (High ischemic correlation)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fbs = forms.ChoiceField(
        label='Fasting Blood Sugar > 120 mg/dL',
        choices=[(0, 'No (Fasting Sugar ≤ 120 mg/dL)'), (1, 'Yes (Fasting Sugar > 120 mg/dL)')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class KidneyPredictionForm(forms.Form):
    sc = forms.FloatField(
        label='Serum Creatinine (mg/dL)',
        min_value=0.2, max_value=18.0, initial=1.1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text='Standard Reference: 0.7 - 1.3 mg/dL'
    )
    bu = forms.FloatField(
        label='Blood Urea Nitrogen (mg/dL)',
        min_value=5.0, max_value=350.0, initial=34.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        help_text='Standard Reference: 7 - 20 mg/dL'
    )
    al = forms.ChoiceField(
        label='Urinary Albumin (Proteinuria)',
        choices=[
            (0, 'Nil / Normal (0)'),
            (1, 'Trace (+1)'),
            (2, 'Moderate (+2)'),
            (3, 'High (+3)'),
            (4, 'Very High (+4)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    hemo = forms.FloatField(
        label='Blood Hemoglobin (g/dL)',
        min_value=3.0, max_value=22.0, initial=13.5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text='Normal: 12.0 - 17.5 g/dL'
    )
    bp = forms.FloatField(
        label='Blood Pressure (mm Hg)',
        min_value=50.0, max_value=200.0, initial=78.0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Resting diastolic pressure'
    )
    sg = forms.ChoiceField(
        label='Urine Specific Gravity',
        choices=[
            (1.025, '1.025 (Well concentrated)'),
            (1.020, '1.020 (Normal)'),
            (1.015, '1.015 (Mildly dilute)'),
            (1.010, '1.010 (Isosthenuria - Fixed)'),
            (1.005, '1.005 (Severely dilute)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    age = forms.IntegerField(
        label='Age (Years)',
        min_value=10, max_value=115, initial=48,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    sod = forms.FloatField(
        label='Serum Sodium (mEq/L)',
        min_value=100.0, max_value=175.0, initial=139.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        help_text='Normal: 135 - 145 mEq/L'
    )
    pot = forms.FloatField(
        label='Serum Potassium (mEq/L)',
        min_value=2.0, max_value=8.5, initial=4.4,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text='Normal: 3.5 - 5.0 mEq/L'
    )
