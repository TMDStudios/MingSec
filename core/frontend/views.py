from django.shortcuts import render, redirect
from base.models import CamRequest, AlarmReport, StatusReport

def index(request):
    return render(request, 'index.html')

def submitCamRequest(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    
    cam_type = request.POST['type']
    camera = request.POST['camera']
    ip = get_client_ip(request)
    length = 10000 # in milliseconds

    if cam_type == 'video':
        try:
            form_length = int(request.POST['length'])*1000
            if form_length > 0 and form_length < 60000:
                length = form_length
        except ValueError:
            pass

    camRequest = CamRequest(type=cam_type, camera=camera, ip=ip, length=length)
    camRequest.save()

    return redirect("frontend:index")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip