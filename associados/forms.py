from django.forms import ModelForm
from associados.models import Associados


class AssociadosForm(ModelForm):
    class Meta:
        model = Associados
        fields = [
            'nome',
            'sobrenome',
            'tipo',
            'valor_mensalidade',
        ]


