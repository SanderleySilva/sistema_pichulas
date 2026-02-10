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





def tipo_relatorio(request):
    return render(request, 'tipo_relatorio.html')




def relatorio_mensal(request):
    if request.method == 'GET':
        form = RelatorioMensalForm()
        return render(request, 'selecionar_mes.html', {'form': form})

    if request.method == 'POST':
        form = RelatorioMensalForm(request.POST)

        if form.is_valid():
            mes = int(form.cleaned_data['meses'])
            ano = form.cleaned_data['ano']

            # Querysets separados
            mensalidades_pagas = Mensalidade.objects.filter(
                mes=mes, ano=ano, status="PAGA"
            ).order_by('associado__nome')

            mensalidades_pendentes = Mensalidade.objects.filter(
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
            style_title = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18,
                                         textColor=colors.HexColor("#2c3e50"), spaceAfter=12)
            style_heading = ParagraphStyle('Heading', parent=styles['Heading3'], fontSize=12,
                                           textColor=colors.HexColor("#2c3e50"), spaceBefore=15, spaceAfter=10)
            style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
            style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=12, spaceAfter=10)

            # --- Cabeçalho ---
            elements.append(Paragraph(f"RELATÓRIO MENSAL DE MENSALIDADES", style_title))
            elements.append(Paragraph("<b>Período de Referência:</b>", style_label))
            elements.append(Paragraph(f"{mes:02d}/{ano}", style_value))
            elements.append(Spacer(1, 0.1 * inch))

            # Função auxiliar para criar o estilo padrão de tabela
            def get_pichulas_table_style(header_color):
                return TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), header_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 10),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
                ])

            col_widths = [4.5 * inch, 2.5 * inch]

            # --- Tabela 1: PAGOS ---
            elements.append(Paragraph("<i class='bi bi-check-circle'></i> PAGAMENTOS CONFIRMADOS", style_heading))
            data_pagos = [['ASSOCIADO', 'VALOR PAGO']]
            for m in mensalidades_pagas:
                data_pagos.append([f"{m.associado.nome} {m.associado.sobrenome}".upper(), f"R$ {m.valor:,.2f}"])

            if len(data_pagos) > 1:
                t_pagos = Table(data_pagos, colWidths=col_widths)
                t_pagos.setStyle(get_pichulas_table_style(colors.HexColor("#27ae60")))  # Verde para Pagos
                elements.append(t_pagos)
            else:
                elements.append(Paragraph("Nenhum pagamento registrado.", styles['Italic']))

            # --- Tabela 2: NÃO PAGOS ---
            elements.append(Paragraph("PAGAMENTOS PENDENTES", style_heading))
            data_pendentes = [['ASSOCIADO', 'VALOR EM ABERTO']]
            for m in mensalidades_pendentes:
                data_pendentes.append([f"{m.associado.nome} {m.associado.sobrenome}".upper(), f"R$ {m.valor:,.2f}"])

            if len(data_pendentes) > 1:
                t_pendentes = Table(data_pendentes, colWidths=col_widths)
                t_pendentes.setStyle(get_pichulas_table_style(colors.HexColor("#e74c3c")))  # Vermelho para Pendentes
                elements.append(t_pendentes)
            else:
                elements.append(Paragraph("Não há pendências para este mês.", styles['Italic']))

            elements.append(Spacer(1, 0.4 * inch))

            # --- Resumo Financeiro Final ---
            resumo_data = [
                ['RESUMO FINANCEIRO', ''],
                ['Total Recebido:', f"R$ {total_arrecadado:,.2f}"],
                ['Total em Aberto:', f"R$ {total_pendente:,.2f}"],
                ['Expectativa Total:', f"R$ {total_geral:,.2f}"]
            ]

            resumo_table = Table(resumo_data, colWidths=[2 * inch, 1.5 * inch])
            resumo_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 1), (1, 1), colors.darkgreen),
                ('TEXTCOLOR', (0, 2), (1, 2), colors.red),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ]))

            elements.append(Table([[Spacer(1, 1), resumo_table]], colWidths=[3.5 * inch, 3.5 * inch]))

            # Rodapé
            elements.append(Spacer(1, 0.5 * inch))
            elements.append(Paragraph("<font color='grey' size='8'>Associação Pichulas - Gerado automaticamente</font>",
                                      styles['Normal']))

            doc.build(elements)
            return response


def selecionar_ano(request):
    form = SelecionarAnoForm()
    return render(request, 'selecionar_ano.html', {'form': form})



def relatorio_anual_pdf(request):
    # 1️⃣ Pegar o ano enviado pelo formulário
    ano_param = request.GET.get('ano')

    if not ano_param:
        return HttpResponse("Ano não informado.")

    try:
        ano = int(ano_param)
    except ValueError:
        return HttpResponse("Ano inválido.")

    # 2️⃣ Criar resposta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_anual_{ano}.pdf"'

    # Configuração do Documento (Margens Padronizadas)
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    # Estilos Customizados Pichulas
    style_title = ParagraphStyle(
        'CustomTitle', parent=styles['Title'], fontSize=18, textColor=colors.HexColor("#2c3e50"), spaceAfter=12
    )
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=12, spaceAfter=10)

    # 3️⃣ Cabeçalho
    elements.append(Paragraph(f"RELATÓRIO ANUAL DE ARRECADAÇÃO", style_title))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph("<b>Exercício:</b>", style_label))
    elements.append(Paragraph(f"{ano}", style_value))
    elements.append(Spacer(1, 0.2 * inch))

    # 4️⃣ Buscar mensalidades pagas (Ajustado para 'PAGA' conforme padrão anterior)
    mensalidades = Mensalidade.objects.filter(ano=ano, status='PAGA')

    # 5️⃣ Agrupar por mês e somar
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

    # Cabeçalho da Tabela
    data = [['MÊS DE REFERÊNCIA', 'TOTAL ARRECADADO']]

    total_anual = Decimal('0.00')

    # 7️⃣ Preencher tabela com formatação
    for item in resumo:
        total_mes = item['total'] or Decimal('0.00')
        data.append([
            MESES_DICT.get(item['mes'], str(item['mes'])).upper(),
            f"R$ {total_mes:,.2f}"
        ])
        total_anual += total_mes

    # 9️⃣ Estilização da Tabela
    table = Table(data, colWidths=[4.0 * inch, 3.0 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Valores à direita
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # Resumo Final (Total Anual)
    resumo_data = [
        ['FECHAMENTO ANUAL', ''],
        ['Total Acumulado:', f"R$ {total_anual:,.2f}"]
    ]

    resumo_table = Table(resumo_data, colWidths=[2 * inch, 1.5 * inch])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 1), (1, 1), colors.darkgreen),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))

    elements.append(Table([[Spacer(1, 1), resumo_table]], colWidths=[3.5 * inch, 3.5 * inch]))

    # Rodapé
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("<font color='grey' size='8'>Associação Pichulas - Relatório Anual Consolidado</font>",
                              styles['Normal']))

    doc.build(elements)
    return response


