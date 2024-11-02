from django.shortcuts import render, redirect
from .forms import CamRequestForm
from base.models import CamRequest, AlarmReport, StatusReport
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .dropbox_handler import DropboxHandler
from django.http import JsonResponse

from dotenv.main import load_dotenv
import os
import logging

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()
DROPBOX_APP_KEY_RW = os.environ['DROPBOX_APP_KEY_RW']
DROPBOX_APP_SECRET_RW = os.environ['DROPBOX_APP_SECRET_RW']
DROPBOX_REFRESH_TOKEN_RW = os.environ['DROPBOX_REFRESH_TOKEN_RW']
dropbox_handler = DropboxHandler(DROPBOX_APP_KEY_RW, DROPBOX_APP_SECRET_RW, DROPBOX_REFRESH_TOKEN_RW, logger)

@login_required
def home(request):
    """Render the home page without fetching logs server-side."""
    log_files = []

    form = CamRequestForm()
    return render(request, 'home.html', {'form': form, 'log_files': log_files})

@login_required
def fetch_log_files(request):
    """Fetch log files from Dropbox."""
    log_files = []

    if dropbox_handler.connected:
        if dropbox_handler.get_logs() == "OK":
            log_files = dropbox_handler.log_files
        else:
            logger.error("UNABLE TO FETCH LOGS")

    return JsonResponse({'log_files': log_files})

@login_required
def fetch_log(request):
    """Fetch log data for a specific log file."""
    log_file = request.GET.get('log_file', 'log.txt')
    log_data = []

    if dropbox_handler.connected:
        log_data = dropbox_handler.view_log(log_file)

    return JsonResponse({'log_data': log_data})

def login(request):
    """Handle user login and redirect to home page on success."""
    form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('frontend:home')

    return render(request, 'login.html', {'form': form})

@login_required
def submitCamRequest(request):
    """Process the camera request form and save the request."""
    if request.method=='POST':
        form = CamRequestForm(request.POST)
        if form.is_valid():
            cam_type = form.cleaned_data['cam_type']
            camera = form.cleaned_data['camera']
            length = form.cleaned_data.get('length', 10) * 1000  # Defaults to 10 seconds if not provided
            ip = get_client_ip(request)
            
            camRequest = CamRequest(type=cam_type, camera=camera, ip=ip, length=length)
            camRequest.save()
            return JsonResponse({'message': 'Camera request submitted successfully!'})
        else:
            return JsonResponse({'message': 'Failed to submit request. Invalid form.'}, status=400)

def get_client_ip(request):
    """Retrieve the client's IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip