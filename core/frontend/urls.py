from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('request/', views.submitCamRequest, name='submitCamRequest'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('fetch-log/', views.fetch_log, name='fetch_log'),
]