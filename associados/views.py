from django.shortcuts import render, redirect, get_object_or_404
from associados.models import Associados
from associados.forms import AssociadosForm


def cadastrar_associado(request):
    if request.method == 'POST':
        form = AssociadosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_associados')
    else:
        form = AssociadosForm()
    return render(request, 'cadastrar_associados.html',{'form':form})



def lista_associados(request):
    associados = Associados.objects.all()
    return render(request, 'lista_associados.html',{'associados':associados})



def remover_associado(request,id):
    associado = get_object_or_404(Associados,id=id)
    associado.delete()
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

    mensalidade = associado.mensalidades.all().order_by('ano', 'mes')

    context = {'associado':associado,'mesalidade':mensalidade}

    return render(request, 'detalhe_associado.html',context)