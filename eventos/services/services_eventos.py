

from associados.models import Associados
from eventos.models import EventoAssociacao


class GerarParticipantesEventoService:
    """
    Serviço para gerar automaticamente participantes de um evento.

    Esta classe é responsável por criar registros de participação
    (EventoAssociacao) para todos os associados ativos de uma associação
    quando um novo evento é criado.
    """

    def __init__(self, evento):
        self.evento = evento

    def executar(self):
        """
        Executa a criação de participantes para o evento.

        Busca todos os associados ativos da associação do evento e cria
        registros de EventoAssociacao para cada um, definindo o valor
        devido conforme a cota do evento.

        Returns:
            None
        """

        associados_ativos = Associados.objects.filter(
            associacao = self.evento.associacao,
            ativo=True)
        for associado in associados_ativos:
            EventoAssociacao.objects.create(
                eventos=self.evento,
                associado=associado,
                valor_devido=self.evento.valor_da_cota,
                valor_pago = 0
            )
