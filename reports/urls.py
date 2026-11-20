from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_history, name='history'),
    path('upload/', views.upload_report, name='upload'),
    path('confirm/<int:pk>/', views.confirm_extracted_data, name='confirm'),
    path('detail/<int:pk>/', views.report_detail, name='detail'),
    path('delete/<int:pk>/', views.delete_report, name='delete'),
    path('download/<int:pk>/', views.download_report_pdf, name='download_pdf'),
    path('compare/', views.compare_reports, name='compare'),
]
