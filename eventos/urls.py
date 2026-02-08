from django.urls import path
from . import views

urlpatterns = [
    path('criar_eventos/', views.criar_evento, name='criar_evento'),
    path('lista_eventos', views.lista_eventos, name='lista_eventos'),
]