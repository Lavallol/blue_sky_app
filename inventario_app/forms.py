from django import forms
from .models import Producto, ConteoSesion, ConteoLinea


# ---------------------------------------------------------
# FORMULARIO DE PRODUCTO
# ---------------------------------------------------------

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'


# ---------------------------------------------------------
# FORMULARIOS DE APLICONTEO PROFESIONAL
# ---------------------------------------------------------

class ConteoSesionForm(forms.ModelForm):
    class Meta:
        model = ConteoSesion
        fields = ['usuario', 'observaciones']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ConteoLineaForm(forms.ModelForm):
    class Meta:
        model = ConteoLinea
        fields = [
            'producto',
            'stock_teorico',
            'stock_contado',
            'motivo',
            'ubicacion',
        ]
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'stock_teorico': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_contado': forms.NumberInput(attrs={'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
        }