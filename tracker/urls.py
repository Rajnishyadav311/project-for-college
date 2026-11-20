from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.tracker_dashboard, name='dashboard'),
    path('add/', views.add_measurement, name='add'),
    path('edit/<int:pk>/', views.edit_measurement, name='edit'),
    path('delete/<int:pk>/', views.delete_measurement, name='delete'),
]
