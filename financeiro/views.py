from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from .models import Mensalidade
from .forms import RelatorioMensalForm, SelecionarAnoForm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime

# Definição de Cores do Tema (Verde - Gestão Esportiva)
COR_PRIMARIA = colors.HexColor("#1a4d2e")
COR_SECUNDARIA = colors.HexColor("#f8f9fa")
COR_TEXTO = colors.HexColor("#333333")
COR_SUCESSO = colors.HexColor("#198754")
COR_PENDENTE = colors.HexColor("#dc3545")


@login_required(login_url='/login/')
def tipo_relatorio(request):
    return render(request, 'tipo_relatorio.html')


@login_required(login_url='/login/')
def relatorio_mensal(request):
    if request.method == 'GET':
        form = RelatorioMensalForm()
        return render(request, 'selecionar_mes.html', {'form': form})

    if request.method == 'POST':
        form = RelatorioMensalForm(request.POST)

        if form.is_valid():
            mes = int(form.cleaned_data['meses'])
            ano = form.cleaned_data['ano']

            # Obtém a associação do usuário logado dinamicamente
            associacao_obj = request.user.perfil.associacao
            nome_associacao = associacao_obj.nome if associacao_obj else "Gestão Esportiva"

            # Querysets
            mensalidades_pagas = Mensalidade.objects.filter(
                associacao=associacao_obj,
                mes=mes, ano=ano, status="PAGA"
            ).order_by('associado__nome')

            mensalidades_pendentes = Mensalidade.objects.filter(
                associacao=associacao_obj,
                mes=mes, ano=ano
            ).exclude(status="PAGA").order_by('associado__nome')

            # Cálculos Financeiros
            total_arrecadado = mensalidades_pagas.aggregate(total=Sum('valor'))['total'] or 0
            total_pendente = mensalidades_pendentes.aggregate(total=Sum('valor'))['total'] or 0
            total_geral = total_arrecadado + total_pendente

            # Configuração do Response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="relatorio_mensal_{mes}_{ano}.pdf"'

            doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
            elements = []
            styles = getSampleStyleSheet()

            # Estilos Customizados
            style_title = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16,
                                         textColor=COR_PRIMARIA, spaceAfter=2, leading=20)
            style_subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10,
                                            textColor=colors.grey, alignment=1, spaceAfter=20)
            style_heading = ParagraphStyle('Heading', parent=styles['Heading3'], fontSize=12,
                                           textColor=COR_TEXTO, spaceBefore=15, spaceAfter=10)
            style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
            style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=12, spaceAfter=10)

            # --- Cabeçalho ---
            elements.append(Paragraph(f"RELATÓRIO MENSAL", style_title))
            elements.append(Paragraph(f"{nome_associacao}", style_subtitle))

            elements.append(Paragraph("<b>Período de Referência:</b>", style_label))
            elements.append(Paragraph(f"{mes:02d}/{ano}", style_value))
            elements.append(Spacer(1, 0.1 * inch))

            # Função auxiliar de estilo de tabela
            def get_custom_table_style(header_bg_color):
                return TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), header_bg_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Valores à direita
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
                ])

            col_widths = [4.5 * inch, 2.5 * inch]

            # --- Tabela 1: PAGOS ---
            elements.append(Paragraph("PAGAMENTOS RECEBIDOS", style_heading))
            data_pagos = [['ASSOCIADO / ATLETA', 'VALOR PAGO']]
            for m in mensalidades_pagas:
                data_pagos.append([f"{m.associado.nome} {m.associado.sobrenome}".upper(), f"R$ {m.valor:,.2f}"])

            if len(data_pagos) > 1:
                t_pagos = Table(data_pagos, colWidths=col_widths)
                t_pagos.setStyle(get_custom_table_style(COR_PRIMARIA))  # Verde Institucional
                elements.append(t_pagos)
            else:
                elements.append(Paragraph("Nenhum pagamento registrado neste período.", styles['Italic']))

            # --- Tabela 2: PENDENTES ---
            elements.append(Paragraph("PENDÊNCIAS FINANCEIRAS", style_heading))
            data_pendentes = [['ASSOCIADO / ATLETA', 'VALOR EM ABERTO']]
            for m in mensalidades_pendentes:
                data_pendentes.append([f"{m.associado.nome} {m.associado.sobrenome}".upper(), f"R$ {m.valor:,.2f}"])

            if len(data_pendentes) > 1:
                t_pendentes = Table(data_pendentes, colWidths=col_widths)
                t_pendentes.setStyle(get_custom_table_style(
                    colors.HexColor("#6c757d")))  # Cinza para pendentes (menos alarmante, mas sério)
                elements.append(t_pendentes)
            else:
                elements.append(Paragraph("Não há pendências registradas.", styles['Italic']))

            elements.append(Spacer(1, 0.4 * inch))

            # --- Resumo Financeiro ---
            resumo_data = [
                ['RESUMO DO PERÍODO', ''],
                ['Total Recebido:', f"R$ {total_arrecadado:,.2f}"],
                ['Total em Aberto:', f"R$ {total_pendente:,.2f}"],
                ['Potencial Total:', f"R$ {total_geral:,.2f}"]
            ]

            resumo_table = Table(resumo_data, colWidths=[2 * inch, 1.5 * inch])
            resumo_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 1), (1, 1), COR_SUCESSO),
                ('TEXTCOLOR', (0, 2), (1, 2), COR_PENDENTE),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))

            elements.append(Table([[Spacer(1, 1), resumo_table]], colWidths=[3.5 * inch, 3.5 * inch]))

            # Rodapé Dinâmico
            elements.append(Spacer(1, 0.5 * inch))
            elements.append(Paragraph(f"<font color='grey' size='8'>{nome_associacao} - Documento Oficial</font>",
                                      styles['Normal']))

            doc.build(elements)
            return response


@login_required(login_url='/login')
def selecionar_ano(request):
    form = SelecionarAnoForm()
    return render(request, 'selecionar_ano.html', {'form': form})


@login_required(login_url='/login')
def relatorio_anual_pdf(request):
    ano_param = request.GET.get('ano')

    if not ano_param:
        return HttpResponse("Ano não informado.")

    try:
        ano = int(ano_param)
    except ValueError:
        return HttpResponse("Ano inválido.")

    # Obtém a associação do usuário logado dinamicamente
    associacao_obj = request.user.perfil.associacao
    nome_associacao = associacao_obj.nome if associacao_obj else "Gestão Esportiva"

    # Criar resposta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_anual_{ano}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    # Estilos Customizados
    style_title = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16, textColor=COR_PRIMARIA,
                                 spaceAfter=2, leading=20)
    style_subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey,
                                    alignment=1, spaceAfter=20)
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=12, spaceAfter=10)

    # Cabeçalho
    elements.append(Paragraph(f"RELATÓRIO ANUAL CONSOLIDADO", style_title))
    elements.append(Paragraph(f"{nome_associacao}", style_subtitle))

    elements.append(Paragraph("<b>Exercício Fiscal:</b>", style_label))
    elements.append(Paragraph(f"{ano}", style_value))
    elements.append(Spacer(1, 0.2 * inch))

    # Buscar mensalidades pagas
    mensalidades = Mensalidade.objects.filter(
        associacao=associacao_obj,
        ano=ano, status='PAGA'
    )

    # Agrupar por mês e somar
    resumo = (
        mensalidades
        .values('mes')
        .annotate(total=Sum('valor'))
        .order_by('mes')
    )

    MESES_DICT = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
    }

    data = [['MÊS DE REFERÊNCIA', 'TOTAL ARRECADADO']]
    total_anual = Decimal('0.00')

    # Preencher tabela
    for item in resumo:
        total_mes = item['total'] or Decimal('0.00')
        data.append([
            MESES_DICT.get(item['mes'], str(item['mes'])).upper(),
            f"R$ {total_mes:,.2f}"
        ])
        total_anual += total_mes

    # Se não houver dados, adiciona uma linha vazia ou mensagem
    if len(data) == 1:
        data.append(["Sem registros no ano", "R$ 0,00"])

    # Estilização da Tabela
    table = Table(data, colWidths=[4.0 * inch, 3.0 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COR_PRIMARIA),  # Verde Institucional
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # Resumo Final
    resumo_data = [
        ['BALANÇO ANUAL', ''],
        ['Total Acumulado:', f"R$ {total_anual:,.2f}"]
    ]

    resumo_table = Table(resumo_data, colWidths=[2 * inch, 1.5 * inch])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 1), (1, 1), COR_SUCESSO),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))

    elements.append(Table([[Spacer(1, 1), resumo_table]], colWidths=[3.5 * inch, 3.5 * inch]))

    # Rodapé Dinâmico
    elements.append(Spacer(1, 0.5 * inch))
    current_year = datetime.now().year
    elements.append(
        Paragraph(f"<font color='grey' size='8'>{nome_associacao} - Sistema de Gestão © {current_year}</font>",
                  styles['Normal']))

    doc.build(elements)
    return response