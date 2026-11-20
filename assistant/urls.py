from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.chat_page, name='chat'),
    path('api/send/', views.api_send_message, name='api_send'),
    path('api/clear/', views.api_clear_chat, name='api_clear'),
]
