from . import views
from django.urls import path

urlpatterns = [
    path('tipo_relatorio/', views.tipo_relatorio, name='tipo_relatorio'),
    path('selecionar_mes/', views.relatorio_mensal, name='selecionar_mes'),
    path('selecionar_ano/', views.selecionar_ano, name='selecionar_ano'),
    path('relatorio_anual/', views.relatorio_anual_pdf, name='relatorio_anual'),
]