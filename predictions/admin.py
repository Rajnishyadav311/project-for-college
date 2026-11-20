from django.contrib import admin
from .models import PredictionRecord

@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'disease_type', 'risk_score', 'risk_level', 'created_at')
    list_filter = ('disease_type', 'risk_level')
    search_fields = ('user__username', 'user__email')
