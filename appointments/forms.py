from django import forms
from django.utils import timezone
from .models import Appointment, DoctorReview

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'time_slot', 'symptoms_reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
            'symptoms_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your symptoms, duration, and any previous diagnosis...'}),
        }

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be scheduled in the past.")
        return date


class DoctorAppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'doctor_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctor_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Add diagnostic findings, recommended tests, or lifestyle instructions...'}),
        }


class DoctorReviewForm(forms.ModelForm):
    class Meta:
        model = DoctorReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience with Dr...'}),
        }


class DoctorReplyForm(forms.ModelForm):
    class Meta:
        model = DoctorReview
        fields = ['doctor_reply']
        widgets = {
            'doctor_reply': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Type your professional reply to the patient...'}),
        }
