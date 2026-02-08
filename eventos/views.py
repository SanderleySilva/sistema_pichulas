from django.shortcuts import render, redirect
from eventos.services.services_eventos import GerarParticipantesEventoService
from .forms import EventoForm
from eventos.models import EventoAssociacao, Eventos



def criar_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save()
            GerarParticipantesEventoService(evento).executar()
            return redirect('lista_eventos')

    else:
        form = EventoForm()

    return render(request, 'criar_eventos.html', {'form': form})


def lista_eventos(request):
    eventos = Eventos.objects.all().order_by('-data_evento')

    context = {'eventos': eventos}

    return render(request, 'lista_eventos.html', context)