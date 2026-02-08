from associados.models import Associados
from financeiro.models import Mensalidade
import calendar
from datetime import date


class GerarMensalidadesService:

    def __init__(self, associado):
        self.associado = associado

    def executar(self):
        data_cadastro = self.associado.data_cadastro
        mes_inicio = self.associado.data_cadastro.month
        ano = data_cadastro.year

        for mes in range(mes_inicio, 13):
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            data_vencimento = date(ano, mes, ultimo_dia)

            Mensalidade.objects.get_or_create(
                associado=self.associado,
                mes=mes,
                ano=ano,
                defaults={
                    'valor': self.associado.valor_mensalidade,
                    'status': 'ABERTA',
                    'data_vencimento': data_vencimento,
                }
            )