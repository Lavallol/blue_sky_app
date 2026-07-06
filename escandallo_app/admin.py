from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from django import forms
from django.templatetags.static import static   # ← LÍNEA AÑADIDA
from django.utils.safestring import mark_safe   # ← IMPORT NECESARIO

from .models import Escandallo, EscandalloLinea


# ============================================================
# FORMULARIO INLINE → convierte precio_coste en <input readonly>
# ============================================================
class EscandalloLineaForm(forms.ModelForm):
    class Meta:
        model = EscandalloLinea
        fields = "__all__"
        widgets = {
            "precio_coste": forms.TextInput(attrs={"readonly": "readonly"}),
        }


# ============================================================
# INLINE DEL ESCANDALLO
# ============================================================
class EscandalloLineaInline(admin.TabularInline):
    model = EscandalloLinea
    form = EscandalloLineaForm
    extra = 1

    fields = (
        "producto",
        "cantidad",
        "unidad",
        "merma_porcentaje",
        "precio_coste",
        "cantidad_neta",
        "coste_teorico",
        "coste_real",
        "recargar",
    )

    readonly_fields = (
        "cantidad_neta",
        "coste_teorico",
        "coste_real",
        "recargar",
    )

    # Botón de recargar inline (sin F5)
    def recargar(self, obj):
        return mark_safe('<a class="button" href="javascript:location.reload()">🔄</a>')
    recargar.short_description = "Actualizar"

    # 🔧 PARCHE DEFINITIVO: cargar JS correctamente en el inline
    class Media:
        js = (
            static("admin/js/jquery.init.js"),      # asegura que Select2 esté listo
            static("escandallo/autoprecio_v2.js"),  # tu JS real
        )


# ============================================================
# ADMIN PRINCIPAL DEL ESCANDALLO
# ============================================================
@admin.register(Escandallo)
class EscandalloAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "rendimiento",
        "precio_venta_sin_iva",
        "coste_total",
        "coste_por_racion",
        "margen_unitario",
        "porcentaje_coste",
    )

    readonly_fields = (
        "coste_total",
        "coste_por_racion",
        "margen_unitario",
        "porcentaje_coste",
    )

    inlines = [EscandalloLineaInline]

    # 🔧 También aquí, por seguridad
    class Media:
        js = (
            static("admin/js/jquery.init.js"),
        )
