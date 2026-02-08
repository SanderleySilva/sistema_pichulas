from django.shortcuts import render, redirect, get_object_or_404
from associados.models import Associados
from associados.forms import AssociadosForm
from financeiro.services.registrar_pagamento_services import RegistrarPagamentoServices
from financeiro.services.gerar_mensalidades_services import GerarMensalidadesService


def cadastrar_associado(request):
    if request.method == 'POST':
        form = AssociadosForm(request.POST)
        if form.is_valid():
            associado = form.save()
            GerarMensalidadesService(associado).executar()
            return redirect('lista_associados')

    else:
        form = AssociadosForm()
    return render(request, 'cadastrar_associados.html',{'form':form})



def lista_associados(request):
    associados = Associados.objects.filter(ativo=True)
    return render(request, 'lista_associados.html',{'associados':associados})

def lista_inativos(request):
    associados = Associados.objects.filter(ativo=False)
    return render(request, 'lista_inativos.html',{'associados':associados})


def ativar_associado_inativo(request, id):
    associados = get_object_or_404(Associados,ativo=False, id=id)
    associados.ativo = True
    associados.save()
    return redirect('lista_inativos')




def remover_associado(request,id):
    associado = get_object_or_404(Associados,id=id)
    associado.ativo = False
    associado.save()
    return redirect('lista_associados')



def editar_associado(request, id):
    associado = get_object_or_404(Associados,id=id)

    if request.method == 'POST':
        form = AssociadosForm(request.POST, instance=associado)
        if form.is_valid():
            form.save()
            return redirect('lista_associados')
    else:
        form = AssociadosForm(instance=associado)
    return render(request, 'cadastrar_associados.html',{'form':form})


def detalhe_associado(request,id):
    associado = get_object_or_404(Associados,id=id)

    mensalidades = associado.mensalidades.all().order_by('ano', 'mes')
    mensalidades_abertas = mensalidades.filter(status='ABERTA')
    total_abertas = mensalidades_abertas.count()

    context = {
        'associado':associado,
        'mensalidades':mensalidades,
        'total_abertas':total_abertas,
    }

    return render(request, 'detalhe_associado.html',context)


def registrar_pagamento(request, id):
    associado = get_object_or_404(Associados,id=id)

    service = RegistrarPagamentoServices(
        associado=associado,
        valor = associado.valor_mensalidade
    )
    service.executar()
    return redirect('detalhe_associado',id)