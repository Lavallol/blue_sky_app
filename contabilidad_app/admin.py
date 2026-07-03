from django.contrib import admin
from .models import (
    CuentaContable,
    Diario,
    Asiento,
    AsientoLinea,
)


# =========================================================
# CUENTAS CONTABLES
# =========================================================

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre")
    search_fields = ("codigo", "nombre")
    ordering = ("codigo",)


# =========================================================
# DIARIOS
# =========================================================

@admin.register(Diario)
class DiarioAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre")
    search_fields = ("codigo", "nombre")
    ordering = ("codigo",)


# =========================================================
# ASIENTOS Y LÍNEAS CONTABLES
# =========================================================

class AsientoLineaInline(admin.TabularInline):
    model = AsientoLinea
    extra = 0
    fields = ("cuenta", "descripcion", "debe", "haber")
    readonly_fields = ()
    ordering = ("id",)


@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ("id", "diario", "fecha", "descripcion", "referencia", "usuario")
    search_fields = ("descripcion", "referencia")
    list_filter = ("diario", "fecha")
    ordering = ("-id",)
    inlines = [AsientoLineaInline]
