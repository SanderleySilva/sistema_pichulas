from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from associados.models import Associados
from eventos.services.services_eventos import GerarParticipantesEventoService
from .forms import EventoForm
from eventos.models import EventoAssociacao, Eventos
from datetime import timezone


from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from eventos.models import Eventos





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
    eventos = Eventos.objects.filter(status='aberto').order_by('-data_evento')

    context = {'eventos': eventos}

    return render(request, 'lista_eventos.html', context)


def lista_eventos_finalizados(request):
    eventos = Eventos.objects.filter(status='finalizado').order_by('-data_evento')
    return render(request, 'lista_eventos_finalizados.html', {'eventos': eventos})


def finalizar_evento(request, id):
    evento = get_object_or_404(Eventos, id=id)
    evento.finalizar_evento()
    return redirect('lista_eventos')


def cancelar_evento(request, id):
    evento = get_object_or_404(Eventos, id=id)
    evento.cancelar_evento()
    return redirect('lista_eventos')


def lista_associados_eventos(request, id):
    evento = get_object_or_404(Eventos, id=id)

    participantes = evento.participantes.select_related('associacao')
    context = {'evento': evento, 'participantes': participantes}

    return render(request, 'participantes_evento.html', context)


def pagamento_cota(request, id):
    participante = get_object_or_404(EventoAssociacao, id=id)

    if request.method == 'POST':
        valor= request.POST.get('valor')

        if valor:
            valor = Decimal(valor)

        participante.valor_pago += valor

        if participante.valor_pago > participante.valor_devido:
            participante.valor_pago = participante.valor_devido

        participante.save()

    return redirect('lista_associados_eventos', participante.eventos.id)


from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse


def relatorio_evento_pdf(request, id):
    evento = get_object_or_404(Eventos, id=id)
    participantes = evento.participantes.all()

    # Cálculos para o resumo
    total_devido = sum(p.valor_devido for p in participantes)
    total_pago = sum(p.valor_pago for p in participantes)
    pendente = total_devido - total_pago

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{evento.nome_evento}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    # Estilo Personalizado para o Título e Labels
    style_title = ParagraphStyle(
        'CustomTitle', parent=styles['Title'], fontSize=18, textColor=colors.HexColor("#2c3e50"), spaceAfter=12
    )
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=12, spaceAfter=10)

    # Título do Relatório
    elements.append(Paragraph(f"RELATÓRIO DE EVENTO", style_title))
    elements.append(Spacer(1, 0.1 * inch))

    # Informações do Evento (Grid superior)
    elements.append(Paragraph("<b>Evento:</b>", style_label))
    elements.append(Paragraph(f"{evento.nome_evento}", style_value))

    elements.append(Paragraph("<b>Data e Local:</b>", style_label))
    elements.append(Paragraph(f"{evento.data_evento} - {evento.local_evento}", style_value))

    elements.append(Spacer(1, 0.2 * inch))

    # Tabela de Participantes
    data = [['ASSOCIADO', 'VALOR DEVIDO', 'VALOR PAGO', 'STATUS']]

    for p in participantes:
        status_text = "PAGO" if p.esta_pago else "PENDENTE"
        # Definindo cor do texto do status
        status_color = colors.darkgreen if p.esta_pago else colors.red

        data.append([
            f"{p.associacao.nome} {p.associacao.sobrenome}".upper(),
            f"R$ {p.valor_devido:,.2f}",
            f"R$ {p.valor_pago:,.2f}",
            Paragraph(f"<b>{status_text}</b>",
                      ParagraphStyle('Status', textColor=status_color, fontSize=9, alignment=1))
        ])

    # Configuração da Tabela
    # Ajustando larguras das colunas para ocupar a página A4 (aprox 7.5 polegadas úteis)
    col_widths = [3.5 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch]
    table = Table(data, colWidths=col_widths)

    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),

        # Alinhamento e Fontes das Linhas
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Linhas e Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # Resumo Financeiro no final
    resumo_data = [
        ['RESUMO DO EVENTO', ''],
        ['Total Arrecadado:', f"R$ {total_pago:,.2f}"],
        ['Total Pendente:', f"R$ {pendente:,.2f}"],
        ['Total Geral:', f"R$ {total_devido:,.2f}"]
    ]

    resumo_table = Table(resumo_data, colWidths=[2 * inch, 1.5 * inch])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 1), (0, 1), colors.darkgreen),
        ('TEXTCOLOR', (0, 2), (0, 2), colors.red),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))

    # Alinha o resumo à direita
    elements.append(Table([[Spacer(1, 1), resumo_table]], colWidths=[4 * inch, 3.5 * inch]))

    # Rodapé
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("<font color='grey' size='8'>Associação Pichulas - Sistema de Gestão Interna</font>",
                              styles['Normal']))

    doc.build(elements)
    return response
