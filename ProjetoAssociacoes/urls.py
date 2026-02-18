from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('home.urls')),
    path('associados/',include('associados.urls')),
    path('financeiro/',include('financeiro.urls')),
    path('relatorios/',include('relatorios.urls')),
    path('eventos/',include('eventos.urls')),
    path('core/',include('core.urls')),
]
