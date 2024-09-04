from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import CamRequest, AlarmReport, StatusReport
from .serializers import CamRequestSerializer, AlarmReportSerializer, StatusReportSerializer
from dotenv.main import load_dotenv
import os

load_dotenv()
API_KEY = os.environ['API_KEY']

@api_view(['GET'])
def getCamRequests(request, api_key):
    if api_key == API_KEY:
        cam_requests = CamRequest.objects.all()
        serializer = CamRequestSerializer(cam_requests, many=True)
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['POST'])
def makeCamRequests(request, api_key):
    serializer = CamRequestSerializer(data=request.data)
    if api_key == API_KEY:
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['GET'])
def getAlarmReports(request, api_key):
    if api_key == API_KEY:
        alarm_reports = AlarmReport.objects.all()
        serializer = AlarmReportSerializer(alarm_reports, many=True)
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['POST'])
def addAlarmReport(request, api_key):
    if api_key == API_KEY:
        serializer = AlarmReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['GET'])
def getStatusReports(request, api_key):
    if api_key == API_KEY:
        status_reports = StatusReport.objects.all()
        serializer = StatusReportSerializer(status_reports, many=True)
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['POST'])
def addStatusReport(request, api_key):
    if api_key == API_KEY:
        serializer = StatusReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    return Response("Invalid Key")