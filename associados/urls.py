from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.cadastrar_associado, name='cadastrar_associado'),
    path('listar/', views.lista_associados, name='lista_associados'),
    path('remover/<int:id>', views.remover_associado, name='remover_associado'),
    path('ediar/<int:id>', views.editar_associado, name='editar_associado'),
    path('detatlhe/<int:id>', views.detalhe_associado, name='detalhe_associado'),
]