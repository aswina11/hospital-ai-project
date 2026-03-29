from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from ai_services import views as ai_views

urlpatterns = [
    path('', views.home, name='home'),
    path('doctors/', views.doctors, name='doctors'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Login and Logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('upload/', ai_views.upload_scan, name='upload_scan'),
    path('report/<int:pk>/', ai_views.report_detail, name='report_detail'),
    path('register/', views.register, name='register'),
    path('chat-api/', ai_views.chat_with_ai, name='chat_api'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('staff-portal/', views.admin_dashboard, name='staff_dashboard'),
    path('complete-appointment/<int:pk>/', views.complete_appointment, name='complete_appointment'),
]