from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls'), name='frontend'),
    path('api/', include('api.urls'), name='api'),
]
