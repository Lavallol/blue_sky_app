from django import forms
from appcompras.models import AlbaranCompraLinea

class AlbaranCompraLineaForm(forms.ModelForm):
    class Meta:
        model = AlbaranCompraLinea
        fields = '__all__'
