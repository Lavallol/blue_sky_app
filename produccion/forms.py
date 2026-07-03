from django import forms
from .models import Produccion, ProduccionLinea

class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = ['escandallo', 'responsable', 'rendimiento_real', 'observaciones']
        widgets = {
            'escandallo': forms.Select(attrs={'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'rendimiento_real': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProduccionLineaForm(forms.ModelForm):
    class Meta:
        model = ProduccionLinea
        fields = ['ingrediente', 'cantidad_real', 'unidad', 'merma']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_real': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'merma': forms.NumberInput(attrs={'class': 'form-control'}),
        }