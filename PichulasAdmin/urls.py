from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('adminApp.urls')),
    path('associados/',include('associados.urls')),
    path('financeiro/',include('financeiro.urls')),
    path('relatorios/',include('relatorios.urls')),
]
