from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from associados.models import Associados
from associados.forms import AssociadosForm
from financeiro.services.registrar_pagamento_services import RegistrarPagamentoServices
from financeiro.services.gerar_mensalidades_services import GerarMensalidadesService



@login_required(login_url='login')
def cadastrar_associado(request):

    if request.method == 'POST':
        form = AssociadosForm(request.POST)

        if form.is_valid():
            associado = form.save(commit=False)
            associado.associacao = request.user.perfil.associacao
            associado.save()

            GerarMensalidadesService(associado).executar()

            return redirect('lista_associados')
    else:
        form = AssociadosForm()

    return render(request, 'cadastrar_associados.html', {'form': form})


@login_required(login_url='login')
def lista_associados(request):

    associados = Associados.objects.filter(
        associacao=request.user.perfil.associacao,
        ativo=True
    )

    return render(request, 'lista_associados.html', {'associados': associados})



@login_required(login_url='login')
def lista_inativos(request):


    associados = Associados.objects.filter(
        associacao=request.user.perfil.associacao,
        ativo=False
    )

    return render(request, 'lista_inativos.html', {'associados': associados})



@login_required(login_url='login')
def ativar_associado_inativo(request, id):


    associado = get_object_or_404(
        Associados,
        id=id,
        associacao=request.user.perfil.associacao,
        ativo=False
    )

    associado.ativo = True
    associado.save()

    return redirect('lista_inativos')



@login_required(login_url='login')
def remover_associado(request, id):


    associado = get_object_or_404(
        Associados,
        id=id,
        associacao=request.user.perfil.associacao
    )

    associado.ativo = False
    associado.save()

    return redirect('lista_associados')



@login_required(login_url='login')
def editar_associado(request, id):


    associado = get_object_or_404(
        Associados,
        id=id,
        associacao=request.user.perfil.associacao
    )

    if request.method == 'POST':
        form = AssociadosForm(request.POST, instance=associado)

        if form.is_valid():
            form.save()
            return redirect('lista_associados')
    else:
        form = AssociadosForm(instance=associado)

    return render(request, 'cadastrar_associados.html', {'form': form})



@login_required(login_url='login')
def detalhe_associado(request, id):


    associado = get_object_or_404(
        Associados,
        id=id,
        associacao=request.user.perfil.associacao
    )

    mensalidades = associado.mensalidades.all().order_by('ano', 'mes')
    mensalidades_abertas = mensalidades.filter(status='ABERTA')
    total_abertas = mensalidades_abertas.count()

    context = {
        'associado': associado,
        'mensalidades': mensalidades,
        'total_abertas': total_abertas,
    }

    return render(request, 'detalhe_associado.html', context)



@login_required(login_url='login')
def registrar_pagamento(request, id):

    associado = get_object_or_404(
        Associados,
        id=id,
        associacao=request.user.perfil.associacao
    )

    service = RegistrarPagamentoServices(
        associado=associado,
        valor=associado.valor_mensalidade
    )

    service.executar()

    return redirect('detalhe_associado', id)
