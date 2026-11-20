from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PatientProfile, DoctorProfile

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('MediPredict Role & Details', {'fields': ('role', 'phone', 'gender', 'date_of_birth', 'profile_picture')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
