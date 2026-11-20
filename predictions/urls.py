from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('', views.predict_home, name='home'),
    path('diabetes/', views.predict_diabetes, name='diabetes'),
    path('heart/', views.predict_heart, name='heart'),
    path('kidney/', views.predict_kidney, name='kidney'),
    path('result/<int:pk>/', views.predict_result, name='result'),
    path('history/', views.prediction_history, name='history'),
]
