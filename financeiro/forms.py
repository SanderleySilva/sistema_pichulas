from django import forms


MESES = [
    (1, 'janeiro'),
    (2, 'fevereiro'),
    (3, 'março'),
    (4, 'abril'),
    (5, 'maio'),
    (6, 'junho'),
    (7, 'julho'),
    (8, 'agosto'),
    (9, 'setembro'),
    (10, 'outubro'),
    (11, 'novembro'),
    (12, 'dezembro'),
]


class RelatorioMensalForm(forms.Form):
    meses = forms.ChoiceField(choices=MESES)
    ano = forms.IntegerField()


class SelecionarAnoForm(forms.Form):
    ano = forms.IntegerField()