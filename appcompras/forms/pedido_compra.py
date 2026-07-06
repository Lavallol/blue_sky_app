from django import forms
from appcompras.models import PedidoCompraLinea

class PedidoCompraLineaForm(forms.ModelForm):
    class Meta:
        model = PedidoCompraLinea
        fields = '__all__'
