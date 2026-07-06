from django import forms
from .models import Escandallo, EscandalloLinea

class EscandalloForm(forms.ModelForm):
    class Meta:
        model = Escandallo
        fields = ['nombre', 'descripcion', 'rendimiento']


class EscandalloLineaForm(forms.ModelForm):
    class Meta:
        model = EscandalloLinea
        fields = ['producto', 'cantidad', 'unidad']