from eventos.models import Eventos
from django import forms

class EventoForm(forms.ModelForm):

    class Meta:
        model = Eventos
        fields = ['nome_evento', 'data_evento', 'local_evento', 'valor_da_cota']

        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }