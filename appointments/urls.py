from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('find/', views.find_doctors, name='find_doctors'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('book/<int:pk>/', views.book_appointment, name='book'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('doctor-manage/', views.doctor_manage_appointments, name='doctor_manage'),
    path('update/<int:pk>/', views.update_appointment_status, name='update_status'),
    path('review/<int:pk>/', views.add_review, name='add_review'),
    path('review-reply/<int:pk>/', views.doctor_reply_review, name='reply_review'),
]
