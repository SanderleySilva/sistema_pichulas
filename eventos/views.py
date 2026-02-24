from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from eventos.services.services_eventos import GerarParticipantesEventoService
from .forms import EventoForm
from eventos.models import EventoAssociacao, Eventos
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer




@login_required(login_url='/login/')
def criar_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.associacao = request.user.associacao
            evento.save()
            GerarParticipantesEventoService(evento).executar()
            return redirect('lista_eventos')

    else:
        form = EventoForm()

    return render(request, 'criar_eventos.html', {'form': form})

@login_required(login_url='/login/')
def lista_eventos(request):

    eventos = Eventos.objects.filter(associacao=request.user.associacao,status='aberto').order_by('-data_evento')

    context = {'eventos': eventos}

    return render(request, 'lista_eventos.html', context)

@login_required(login_url='/login/')
def lista_eventos_finalizados(request):
    eventos = Eventos.objects.filter(associacao = request.user.perfil.associacao,status='finalizado').order_by('-data_evento')
    return render(request, 'lista_eventos_finalizados.html', {'eventos': eventos})

@login_required(login_url='/login/')
def finalizar_evento(request, id):
    evento = get_object_or_404(Eventos, id=id,associacao = request.user.perfil.associacao)
    evento.finalizar_evento()
    return redirect('lista_eventos')

@login_required(login_url='/login/')
def cancelar_evento(request, id):
    evento = get_object_or_404(Eventos, id=id, associacao = request.user.associacao)
    evento.cancelar_evento()
    return redirect('lista_eventos')

@login_required(login_url='/login/')
def lista_associados_eventos(request, id):
    evento = get_object_or_404(Eventos, id=id, associacao = request.user.perfil.associacao)

    participantes = EventoAssociacao.objects.select_related(
        'eventos',
        'associado'
    ).filter(eventos=evento)
    context = {'evento': evento, 'participantes': participantes}

    return render(request, 'participantes_evento.html', context)

@login_required(login_url='/login/')
def pagamento_cota(request, id):
    participante = get_object_or_404(EventoAssociacao, id=id, eventos__associacao = request.user.associacao)

    if request.method == 'POST':
        valor= request.POST.get('valor')

        try:
            valor = Decimal(valor)
        except (InvalidOperation, ValueError):
            valor = Decimal('0.00')

        participante.valor_pago = valor

        if participante.valor_pago > participante.valor_devido:
            participante.valor_devido = participante.valor_pago

        participante.save()

    return redirect('lista_associados_eventos', participante.eventos.id)



#__________________________________________#
# Definição de Cores do Tema (Verde - Gestão Esportiva)
COR_PRIMARIA = colors.HexColor("#1a4d2e")
COR_SECUNDARIA = colors.HexColor("#f8f9fa")
COR_TEXTO = colors.HexColor("#333333")
COR_SUCESSO = colors.HexColor("#198754")
COR_PENDENTE = colors.HexColor("#dc3545")
COR_ALERTA = colors.HexColor("#ffc107")

@login_required(login_url='/login/')
def relatorio_evento_pdf(request, id):
    # Recupera o evento e garante que pertence à associação do usuário
    associacao_obj = request.user.perfil.associacao
    nome_associacao = associacao_obj.nome if associacao_obj else "Gestão Esportiva"

    evento = get_object_or_404(Eventos, id=id, associacao=associacao_obj)
    participantes = evento.participantes.all().order_by('associado__nome')

    # Cálculos Financeiros
    total_devido = sum(p.valor_devido for p in participantes)
    total_pago = sum(p.valor_pago for p in participantes)
    pendente = total_devido - total_pago

    # Configuração do PDF
    response = HttpResponse(content_type='application/pdf')
    filename = f"Súmula_{evento.nome_evento.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    # --- Estilos Personalizados ---
    style_title = ParagraphStyle(
        'CustomTitle', parent=styles['Title'], fontSize=16, textColor=COR_PRIMARIA, spaceAfter=2, leading=20
    )
    style_subtitle = ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=1, spaceAfter=20
    )
    style_info_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    style_info_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=11, textColor=COR_TEXTO, leading=14)

    # Estilo para Status na Tabela
    style_status_pago = ParagraphStyle('StPago', parent=styles['Normal'], fontSize=8, textColor=COR_SUCESSO,
                                       alignment=1, fontName='Helvetica-Bold')
    style_status_pend = ParagraphStyle('StPend', parent=styles['Normal'], fontSize=8, textColor=COR_PENDENTE,
                                       alignment=1, fontName='Helvetica-Bold')

    # --- Cabeçalho do Relatório ---
    elements.append(Paragraph("RELATÓRIO DE EVENTO / SÚMULA", style_title))
    elements.append(Paragraph(f"{nome_associacao}", style_subtitle))

    # Tabela de Informações do Evento (Layout Grade)
    # Formatação da data
    data_fmt = evento.data_evento.strftime("%d/%m/%Y") if evento.data_evento else "Data não definida"

    # Define cor do status do evento
    status_color = COR_SUCESSO
    status_text = "ABERTO"
    if evento.status == 'finalizado':
        status_color = colors.grey
        status_text = "FINALIZADO"
    elif evento.status == 'cancelado':
        status_color = COR_PENDENTE
        status_text = "CANCELADO"

    info_data = [
        [Paragraph('<b>EVENTO</b>', style_info_label), Paragraph('<b>DATA</b>', style_info_label),
         Paragraph('<b>LOCAL</b>', style_info_label), Paragraph('<b>SITUAÇÃO</b>', style_info_label)],
        [Paragraph(evento.nome_evento, style_info_value), Paragraph(data_fmt, style_info_value),
         Paragraph(evento.local_evento, style_info_value),
         Paragraph(f"<font color='{status_color.hexval()}'><b>{status_text}</b></font>", style_info_value)]
    ]

    t_info = Table(info_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch, 1.2 * inch])
    t_info.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.3 * inch))

    # --- Tabela de Participantes ---
    # Cabeçalho da Tabela
    data = [['ATLETA / CONVOCADO', 'VALOR COTA', 'VALOR PAGO', 'STATUS']]

    for p in participantes:
        # Define estilo do status
        if p.esta_pago:
            p_status = Paragraph("PAGO", style_status_pago)
        else:
            p_status = Paragraph("PENDENTE", style_status_pend)

        # Nome Formatado
        nome_completo = f"{p.associado.nome} {p.associado.sobrenome}".upper()

        data.append([
            Paragraph(f"<font size=9>{nome_completo}</font>", styles['Normal']),
            f"R$ {p.valor_devido:,.2f}",
            f"R$ {p.valor_pago:,.2f}",
            p_status
        ])

    # Configuração visual da Tabela
    col_widths = [3.8 * inch, 1.2 * inch, 1.2 * inch, 1.0 * inch]
    table = Table(data, colWidths=col_widths)

    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), COR_PRIMARIA),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),  # Centraliza cabeçalhos numéricos

        # Corpo
        ('ALIGN', (1, 1), (2, -1), 'RIGHT'),  # Valores financeiros à direita
        ('ALIGN', (3, 1), (-1, -1), 'CENTER'),  # Status centralizado
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e9ecef")),  # Grade sutil
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COR_SECUNDARIA]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # --- Resumo Financeiro ---
    resumo_data = [
        ['RESUMO FINANCEIRO', ''],
        ['Total Arrecadado:', f"R$ {total_pago:,.2f}"],
        ['Pendente Recebimento:', f"R$ {pendente:,.2f}"],
        ['Previsão Total:', f"R$ {total_devido:,.2f}"]
    ]

    resumo_table = Table(resumo_data, colWidths=[2 * inch, 1.5 * inch])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 1), (1, 1), COR_SUCESSO),  # Verde para recebido
        ('TEXTCOLOR', (0, 2), (1, 2), COR_PENDENTE),  # Vermelho para pendente
        ('TEXTCOLOR', (0, 3), (1, 3), COR_TEXTO),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, COR_TEXTO),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    # Alinha a tabela de resumo à direita
    elements.append(Table([[Spacer(1, 1), resumo_table]], colWidths=[3.7 * inch, 3.5 * inch]))

    # --- Rodapé ---
    elements.append(Spacer(1, 0.5 * inch))
    current_year = datetime.now().year
    elements.append(Paragraph(
        f"<font color='grey' size='8'>{nome_associacao} - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
        styles['Normal']))

    doc.build(elements)
    return response