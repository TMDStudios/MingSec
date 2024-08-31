from django.contrib import admin
from .models import CamRequest, AlarmReport, StatusReport

admin.site.register(CamRequest)
admin.site.register(AlarmReport)
admin.site.register(StatusReport)