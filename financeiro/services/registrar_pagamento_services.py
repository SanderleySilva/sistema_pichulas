from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from financeiro.models import Mensalidade, Pagamento, PagamentoMensalidade


class RegistrarPagamentoServices:

    def __init__(self, associado, valor):
        self.associado = associado
        self.valor = Decimal(valor)

    @transaction.atomic
    def executar(self):

        pagamento = Pagamento.objects.create(
            associado=self.associado,
            valor=self.valor,
            data_pagamento=timezone.now().date(),
        )

        valor_disponivel = self.valor + self.associado.saldo_credito

        mensalidades_abertas = Mensalidade.objects.filter(
            associado=self.associado,
            status='ABERTA'
        ).order_by('ano', 'mes')

        for mensalidade in mensalidades_abertas:

            if valor_disponivel >= mensalidade.valor:

                mensalidade.status = 'PAGA'
                mensalidade.data_pagamento = pagamento.data_pagamento
                mensalidade.save()

                PagamentoMensalidade.objects.create(
                    pagamento=pagamento,
                    mensalidade=mensalidade,
                    valor_utilizado=mensalidade.valor
                )

                valor_disponivel -= mensalidade.valor

            else:
                break

        # Atualiza saldo depois do loop
        self.associado.saldo_credito = valor_disponivel
        self.associado.save()

        return pagamento
