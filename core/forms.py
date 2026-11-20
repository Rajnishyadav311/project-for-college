from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, PatientProfile, DoctorProfile

class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], widget=forms.Select(attrs={'class': 'form-select'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'PATIENT'
        if commit:
            user.save()
            PatientProfile.objects.get_or_create(user=user)
        return user


class DoctorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Doctor Email'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    qualification = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MBBS, MD (Medicine)'}))
    specialization = forms.ChoiceField(choices=DoctorProfile.SPECIALIZATIONS, widget=forms.Select(attrs={'class': 'form-select'}))
    license_number = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medical Registration ID'}))
    clinic_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clinic / Hospital Name'}))
    clinic_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full Clinic Address'}))
    city = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    consultation_fee = forms.DecimalField(max_digits=8, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee in INR'}))
    experience_years = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'DOCTOR'
        if commit:
            user.save()
            DoctorProfile.objects.update_or_create(
                user=user,
                defaults={
                    'qualification': self.cleaned_data['qualification'],
                    'specialization': self.cleaned_data['specialization'],
                    'license_number': self.cleaned_data['license_number'],
                    'clinic_name': self.cleaned_data['clinic_name'],
                    'clinic_address': self.cleaned_data['clinic_address'],
                    'city': self.cleaned_data['city'],
                    'consultation_fee': self.cleaned_data['consultation_fee'],
                    'experience_years': self.cleaned_data['experience_years'],
                    'is_verified': False, # Pending admin verification
                }
            )
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['blood_group', 'allergies', 'chronic_conditions', 'emergency_contact_name', 'emergency_contact_phone', 'address', 'city']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'chronic_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['qualification', 'specialization', 'license_number', 'clinic_name', 'clinic_address', 'city', 'consultation_fee', 'experience_years', 'available_days', 'available_time_start', 'available_time_end', 'bio']
        widgets = {
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'clinic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'clinic_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_days': forms.TextInput(attrs={'class': 'form-control'}),
            'available_time_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'available_time_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
