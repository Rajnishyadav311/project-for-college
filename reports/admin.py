from django.contrib import admin
from .models import MedicalReport, LabParameter

class LabParameterInline(admin.TabularInline):
    model = LabParameter
    extra = 0

@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'report_category', 'report_date', 'status', 'total_tests_count', 'abnormal_tests_count')
    list_filter = ('report_category', 'status', 'report_date')
    search_fields = ('title', 'user__username')
    inlines = [LabParameterInline]

@admin.register(LabParameter)
class LabParameterAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'report', 'measured_value', 'unit', 'status')
    list_filter = ('status',)
    search_fields = ('test_name', 'report__title')
