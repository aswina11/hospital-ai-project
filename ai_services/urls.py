from django.urls import path
from . import views

urlpatterns = [
    path('upload-scan/', views.upload_scan, name='upload_scan'),
    path('report/<int:pk>/', views.report_detail, name='report_detail'),
    path('chat-api/', views.chat_with_ai, name='chat_with_ai'),
]
