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
    """Render the home page with log files and the selected log data."""
    log_files = []
    selected_log = ''
    log_data = ''

    current_log = request.session.get('current_log', 0)
    current_log_param = request.GET.get('log_index', None)

    if dropbox_handler.connected:
        if dropbox_handler.get_logs() == "OK":
            log_files = dropbox_handler.log_files

            if current_log_param is not None:
                try:
                    current_log = int(current_log_param)
                    if current_log < 0 or current_log >= len(log_files):
                        logger.warning("Selected log index out of range. Resetting to 0.")
                        current_log = 0
                except ValueError:
                    logger.error("Invalid log index provided")
                    current_log = 0
            
            request.session['current_log'] = current_log
            
            if log_files:
                selected_log = log_files[current_log]
                log_data = dropbox_handler.view_log(selected_log)
        else:
            logger.error("UNABLE TO FETCH LOGS")
    else:
        logger.warning("NO DROPBOX CONNECTION FOUND, ESTABLISHING NEW CONNECTION...")
        dropbox_handler.dbx = dropbox_handler.connect()

    form = CamRequestForm()
    return render(request, 'home.html', {'form': form, 'log_files': log_files, 'log_data': log_data})

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
            return redirect("frontend:home")

def get_client_ip(request):
    """Retrieve the client's IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip