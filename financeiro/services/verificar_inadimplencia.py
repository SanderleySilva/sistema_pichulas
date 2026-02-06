from associados.models import Associados
from financeiro.models import Mensalidade


class VerificarInadimplenteService:

    def executar(self):
        associados_ativos = Associados.objects.filter(ativo=True)

        for associado in associados_ativos:
            self._verificar_associado(associado)

    def _verificar_associado(self, associado):
        mensalidades = Mensalidade.objects.filter(
            associado=associado,
            status='ABERTA'
        ).order_by('ano', 'mes')

        contador = 0
        mes_anterior = None
        ano_anterior = None

        for mensalidae in mensalidades:
            if mes_anterior is None:
                #primeira mensalidade encontrada aqui
                contador = 1

            else:
                if self._eh_mes_consecutivo(
                    mes_anterior,
                    ano_anterior,
                    mensalidae.mes,
                    mensalidae.ano
                ):
                    contador += 1

                else:
                    contador = 1

            if contador >= 12:
                associado.ativo = False
                associado.save()
                break


            mes_anterior = mensalidae.mes
            ano_anterior = mensalidae.ano

    def _eh_mes_consecutivo(self, mes_ant, ano_ant, mes_atual, ano_atual):
         #mesmo ano
        if ano_ant == ano_atual and mes_atual == mes_ant + 1:
            return True

        #troca ano
        if mes_ant == 12 and mes_atual == 1 and ano_atual == ano_ant +1:
            return True

        return False
