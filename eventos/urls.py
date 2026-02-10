from django.urls import path
from . import views

urlpatterns = [
    path('criar_eventos/', views.criar_evento, name='criar_evento'),
    path('lista_eventos', views.lista_eventos, name='lista_eventos'),
    path('finalizar/<int:id>/', views.finalizar_evento, name='finalizar_evento'),
    path('cancelar/<int:id>/', views.cancelar_evento, name='cancelar_evento'),
    path('finalizados', views.lista_eventos_finalizados, name='lista_eventos_finalizados'),
    path('evento/<int:id>/participantes/', views.lista_associados_eventos, name='lista_associados_eventos'),
    path('participante/<int:id>/pagar/', views.pagamento_cota, name='pagamento_cota'),
    path('relatorio/evento/<int:id>/pdf/', views.relatorio_evento_pdf, name='relatorio_evento')



]