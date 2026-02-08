from django.db import models

# Create your models here.
class Eventos(models.Model):

    STATUS_CHOICES = (
        ('aberto', 'ABERTO'),
        ('cancelado', 'CANCELADO'),
        ('finalizado', 'FINALIZADO'),
    )

    nome_evento = models.CharField(max_length=100)
    data_evento = models.DateField()
    local_evento = models.CharField(max_length=100)
    valor_da_cota = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='ABERTO'
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome_evento} - {self.data_evento}'


class EventoAssociacao(models.Model):
    eventos = models.ForeignKey(
        'eventos.Eventos',
        on_delete=models.CASCADE,
        related_name='participantes',
    )

    associacao = models.ForeignKey(
        'associados.Associados',
        on_delete=models.PROTECT,
        related_name='eventos',
    )

    valor_devido = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.eventos} - {self.associacao}'

    @property
    def esta_pago(self):
        return self.valor_pago >= self.valor_devido
