from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('requests/get/', views.getCamRequests),
    path('requests/add/', views.makeCamRequests),
    path('alarms/get/', views.getAlarmReports),
    path('alarms/add/', views.addAlarmReport),
    path('status/get/', views.getStatusReports),
    path('status/add/', views.addStatusReport),
]