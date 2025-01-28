from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('request/', views.submit_cam_request, name='submit_cam_request'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('fetch-log-files/', views.fetch_log_files, name='fetch_log_files'),
    path('fetch-log/', views.fetch_log, name='fetch_log'),
]