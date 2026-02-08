from django.utils import timezone
from django.db import models

#Criação do modelo para cadastrar os associados
class Associados(models.Model):
    TIPO_CHOICES = (
        ('jogador','Jogador'),
        ('torcedor','Torcedor'),
    )

    nome = models.CharField(max_length = 50)
    sobrenome = models.CharField(max_length = 50)
    tipo = models.CharField(max_length = 50, choices = TIPO_CHOICES, blank = True, null = True)

    data_cadastro = models.DateField(default = timezone.now)

    #valor mensal definido no cadastro
    valor_mensalidade = models.DecimalField(max_digits=10, decimal_places=2)

    #positivo = crédito / negativo = dívida
    saldo_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    ativo = models.BooleanField(default = True)

    def __str__(self):
        return f'{self.nome} - {self.sobrenome} - {self.tipo}'

    @property
    def esta_em_dia(self):
        hoje = timezone.now().date()

        return not self.mensalidades.filter(
            status='ABERTA',
            data_vencimento__lt=hoje
        ).exists()