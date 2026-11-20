from django.db import models
from django.conf import settings

class PredictionRecord(models.Model):
    DISEASE_CHOICES = [
        ('diabetes', 'Diabetes Risk Assessment'),
        ('heart', 'Heart Disease Risk Assessment'),
        ('kidney', 'Chronic Kidney Disease Risk Assessment'),
    ]
    RISK_LEVELS = [
        ('Low', 'Low Risk'),
        ('Moderate', 'Moderate Risk'),
        ('High', 'High Risk'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='predictions')
    disease_type = models.CharField(max_length=20, choices=DISEASE_CHOICES)
    input_features = models.JSONField(default=dict, help_text="Validated features passed into the ML model")
    risk_score = models.FloatField(help_text="Estimated percentage risk (0 to 100)")
    risk_level = models.CharField(max_length=15, choices=RISK_LEVELS, default='Low')
    risk_label = models.CharField(max_length=100)
    feature_contributions = models.JSONField(default=list, blank=True, help_text="Top model factors driving this risk prediction")
    model_version = models.CharField(max_length=50, default='MediPredict-RF-1.0')
    is_demo_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_disease_type_display()} ({self.risk_level})"
