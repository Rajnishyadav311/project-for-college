import os
from django import forms
from .models import MedicalReport

class ReportUploadForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['title', 'report_category', 'report_date', 'report_file', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Annual Blood Chemistry Panel'}),
            'report_category': forms.Select(attrs={'class': 'form-select'}),
            'report_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'report_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional patient notes or physician name...'}),
        }

    def clean_report_file(self):
        file = self.cleaned_data.get('report_file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise forms.ValidationError("Unsupported file format. Please upload a PDF, JPG, JPEG, or PNG document.")
            # 10MB limit
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size exceeds 10MB limit. Please upload a smaller document.")
        return file
