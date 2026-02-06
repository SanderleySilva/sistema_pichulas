import calendar
from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone

from associados.models import Associados
from financeiro.models import Mensalidade


class Command(BaseCommand):
    help = 'Gera mensalidades para todos os associados ativos no ano atual'

    def handle(self, *args, **kwargs):
        ano_atual = timezone.now().year
        associados = Associados.objects.filter(ativo=True)

        for associado in associados:
            for mes in range(1, 13):
                ultimo_dia = calendar.monthrange(ano_atual, mes)[1]

                Mensalidade.objects.get_or_create(
                    associado=associado,
                    mes=mes,
                    ano=ano_atual,
                    defaults={
                        'valor': associado.valor_mensalidade,
                        'data_vencimento': date(ano_atual, mes, ultimo_dia),
                        'status': 'ABERTA',
                    }
                )

        self.stdout.write(self.style.SUCCESS(
            f'Mensalidades do ano {ano_atual} geradas com sucesso.'
        ))
