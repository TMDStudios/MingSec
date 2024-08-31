from django.urls import path
from . import views

urlpatterns = [
    path('requests/get/<slug:api_key>', views.getCamRequests),
    path('requests/add/<slug:api_key>', views.makeCamRequests),
    path('alarms/get/<slug:api_key>', views.getAlarmReports),
    path('alarms/add/<slug:api_key>', views.addAlarmReport),
    path('status/get/<slug:api_key>', views.getStatusReports),
    path('status/add/<slug:api_key>', views.addStatusReport),
]