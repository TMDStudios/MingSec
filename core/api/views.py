from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import CamRequest, AlarmReport, StatusReport
from .serializers import CamRequestSerializer, AlarmReportSerializer, StatusReportSerializer
from dotenv.main import load_dotenv
import os

load_dotenv()
API_KEY = os.environ['API_KEY']

def check_api_key(request):
    # Expecting the API key in the 'Authorization' header in the form "Bearer API_KEY"
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.split()[1] == API_KEY:
        return True
    return False

@api_view(['GET'])
def getCamRequests(request):
    if check_api_key(request):
        cam_requests = CamRequest.objects.all()
        serializer = CamRequestSerializer(cam_requests, many=True)
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['POST'])
def makeCamRequests(request):
    serializer = CamRequestSerializer(data=request.data)
    if check_api_key(request):
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['GET'])
def getAlarmReports(request):
    if check_api_key(request):
        alarm_reports = AlarmReport.objects.all()
        serializer = AlarmReportSerializer(alarm_reports, many=True)
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['POST'])
def addAlarmReport(request):
    if check_api_key(request):
        serializer = AlarmReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['GET'])
def getStatusReports(request):
    if check_api_key(request):
        status_reports = StatusReport.objects.all()
        serializer = StatusReportSerializer(status_reports, many=True)
        return Response(serializer.data)
    return Response("Invalid Key")

@api_view(['POST'])
def addStatusReport(request):
    if check_api_key(request):
        serializer = StatusReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    return Response("Invalid Key")