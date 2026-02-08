from associados.models import Associados
from eventos.models import EventoAssociacao


class GerarParticipantesEventoService:

    def __init__(self, evento):
        self.evento = evento

    def executar(self):

        associados_ativos = Associados.objects.filter(ativo=True)
        for associado in associados_ativos:
            EventoAssociacao.objects.create(
                eventos=self.evento,
                associacao=associado,
                valor_devido=self.evento.valor_da_cota,
                valor_pago = 0
            )
