from django.db import models
from associados.models import Associados
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone



class Mensalidade(models.Model):

    STATUS_CHOICES = (
        ('ABERTA','Aberta'),
        ('PAGA','Paga'),
    )

    associado = models.ForeignKey(
        Associados,
        on_delete=models.PROTECT,
        related_name='mensalidades',
    )

    mes = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    ano = models.PositiveIntegerField()

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ABERTA',
    )

    data_vencimento = models.DateField()
    data_pagamento = models.DateField(
        null=True,
        blank=True,
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['associado', 'mes', 'ano'],
                name='unique_mensalidade_por_mes'
            )
        ]
        ordering = ['ano', 'mes']

    def __str__(self):
        return f'{self.associado} - {self.mes}/{self.ano}'


class Pagamento(models.Model):

    associado = models.ForeignKey(
        Associados,
        on_delete=models.PROTECT,
        related_name='pagamentos',
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    data_pagamento = models.DateField(auto_now_add=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.associado} - {self.valor}'





class PagamentoMensalidade(models.Model):

    pagamento = models.ForeignKey(
        Pagamento,
        on_delete=models.CASCADE,
        related_name='mensalidades_quitadas',
    )

    mensalidade = models.ForeignKey(
        Mensalidade,
        on_delete=models.PROTECT,
        related_name='pagamentos_relacionados',
    )

    valor_utilizado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pagamento {self.pagamento.id} → {self.mensalidade.mes}/{self.mensalidade.ano}'
