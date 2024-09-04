from rest_framework import serializers
from base.models import CamRequest, AlarmReport, StatusReport

class CamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CamRequest
        fields = '__all__'

class AlarmReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlarmReport
        fields = '__all__'

class StatusReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusReport
        fields = '__all__'