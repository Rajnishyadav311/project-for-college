from django.db import models
from django.conf import settings
from django.utils import timezone

class MedicalReport(models.Model):
    CATEGORY_CHOICES = [
        ('cbc', 'Complete Blood Count (CBC)'),
        ('cmp', 'Comprehensive Metabolic Panel (CMP)'),
        ('lipid', 'Lipid Profile / Cholesterol Panel'),
        ('kft', 'Kidney Function Test (KFT / RFT)'),
        ('lft', 'Liver Function Test (LFT)'),
        ('diabetes', 'Diabetes / Glycemic Panel (HbA1c & Glucose)'),
        ('thyroid', 'Thyroid Profile (TSH, T3, T4)'),
        ('general', 'General Laboratory Report / Other'),
    ]
    STATUS_CHOICES = [
        ('pending_confirmation', 'Pending Patient Confirmation'),
        ('confirmed', 'Confirmed & Analyzed'),
        ('failed', 'Processing Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_reports')
    title = models.CharField(max_length=200, default='Diagnostic Laboratory Report')
    report_file = models.FileField(upload_to='reports/%Y/%m/')
    report_category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    report_date = models.DateField(default=timezone.now)
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_confirmation')
    extracted_raw_text = models.TextField(blank=True, null=True)
    clinical_summary = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-report_date', '-upload_date']

    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.report_date})"

    @property
    def total_tests_count(self):
        return self.parameters.count()

    @property
    def abnormal_tests_count(self):
        return self.parameters.filter(status__in=['low', 'high']).count()

    @property
    def normal_tests_count(self):
        return self.parameters.filter(status='normal').count()


class LabParameter(models.Model):
    STATUS_CHOICES = [
        ('normal', 'Within Range'),
        ('low', 'Below Range'),
        ('high', 'Above Range'),
        ('context_needed', 'Context Needed'),
        ('unable_to_interpret', 'Unable to Interpret'),
    ]

    report = models.ForeignKey(MedicalReport, on_delete=models.CASCADE, related_name='parameters')
    test_name = models.CharField(max_length=150)
    measured_value = models.FloatField(blank=True, null=True)
    raw_value_str = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    reference_min = models.FloatField(blank=True, null=True)
    reference_max = models.FloatField(blank=True, null=True)
    reference_text = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='normal')
    explanation_en = models.TextField(blank=True, null=True)
    explanation_hi = models.TextField(blank=True, null=True)
    clinical_note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.test_name}: {self.measured_value} {self.unit} ({self.get_status_display()})"
