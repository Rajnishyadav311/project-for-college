from django.db import models
from django.conf import settings
from django.utils import timezone

class HealthMeasurement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tracker_measurements')
    recorded_at = models.DateField(default=timezone.now)
    weight_kg = models.FloatField(help_text="Weight in Kilograms (e.g. 70.5)")
    height_cm = models.FloatField(help_text="Height in Centimeters (e.g. 175.0)")
    bmi = models.FloatField(blank=True, null=True, help_text="Calculated Body Mass Index (kg/m²)")
    bmi_category = models.CharField(max_length=30, blank=True, null=True)
    systolic_bp = models.IntegerField(blank=True, null=True, help_text="Systolic Blood Pressure (mm Hg)")
    diastolic_bp = models.IntegerField(blank=True, null=True, help_text="Diastolic Blood Pressure (mm Hg)")
    blood_glucose = models.FloatField(blank=True, null=True, help_text="Fasting/Random Glucose (mg/dL)")
    heart_rate = models.IntegerField(blank=True, null=True, help_text="Resting Heart Rate (bpm)")
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at', '-created_at']

    def save(self, *args, **kwargs):
        # Calculate BMI automatically only if valid height and weight provided
        if self.weight_kg and self.height_cm and self.height_cm > 0:
            height_m = self.height_cm / 100.0
            calc_bmi = round(self.weight_kg / (height_m * height_m), 1)
            self.bmi = calc_bmi
            if calc_bmi < 18.5:
                self.bmi_category = 'Underweight'
            elif calc_bmi < 25.0:
                self.bmi_category = 'Normal'
            elif calc_bmi < 30.0:
                self.bmi_category = 'Overweight'
            else:
                self.bmi_category = 'Obese'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.recorded_at}) - BMI: {self.bmi}"
