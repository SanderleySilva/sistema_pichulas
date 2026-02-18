from django.db import models
from django.contrib.auth.models import User


class Assoociacao(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome} {self.cidade}'


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    associacao = models.ForeignKey(Assoociacao, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} {self.associacao.nome}'

User.add_to_class(
    "associacao",
    property(lambda u: u.perfil.associacao)
)