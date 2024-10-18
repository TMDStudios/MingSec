from django.shortcuts import render, redirect
from .forms import CamRequestForm
from base.models import CamRequest, AlarmReport, StatusReport
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

def home(request):
    form = CamRequestForm()
    return render(request, 'home.html', {'form': form})

def login(request):
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
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip