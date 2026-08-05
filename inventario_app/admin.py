# =========================================================
# IMPORTS
# =========================================================
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    ConteoSesion,
    ConteoLinea,
    Producto,
    Proveedor,
    IVA,
    Categoria,
    UnidadMedida,
    AsientoContable,
)

# =========================================================
# RESOURCE PARA PRODUCTO (IMPORT/EXPORT)
# =========================================================
class ProductoResource(resources.ModelResource):
    class Meta:
        model = Producto
        fields = (
            'id',
            'codigo_interno',
            'nombre_interno',
            'nombre_proveedor',
            'categoria',
            'unidad_medida',
            'proveedor',
            'iva',
            'precio_compra',
            'codigo_barras',
            'stock_minimo',
            'stock_actual',
            'activo',
        )
        export_order = fields

# =========================================================
# INLINE DE LÍNEAS DE CONTEO
# =========================================================
class ConteoLineaInline(admin.TabularInline):
    model = ConteoLinea
    extra = 0
    autocomplete_fields = ('producto',)

    readonly_fields = (
        'diferencia',
        'importe_teorico',
        'importe_contado',
        'importe_aumenta',
        'importe_disminuye',
    )

    fields = (
        'codigo_barras',
        'producto',
        'precio_coste',
        'stock_teorico',
        'importe_teorico',
        'stock_contado',
        'importe_contado',
        'diferencia',
        'importe_aumenta',
        'importe_disminuye',
        'motivo',
        'ubicacion',
    )

    @admin.display(description="Importe Aumenta")
    def importe_aumenta(self, obj):
        if obj.diferencia > 0:
            return round(obj.diferencia * obj.precio_coste, 2)
        return 0

    @admin.display(description="Importe Disminuye")
    def importe_disminuye(self, obj):
        if obj.diferencia < 0:
            return round(abs(obj.diferencia) * obj.precio_coste, 2)
        return 0

# =========================================================
# ACCIÓN: REABRIR CONTEO
# =========================================================
@admin.action(description="Reabrir conteo seleccionado")
def reabrir_conteo_admin(modeladmin, request, queryset):
    for sesion in queryset:
        if sesion.estado == "cerrada":
            return redirect(f"/inventario/conteo/{sesion.id}/reabrir/")

    modeladmin.message_user(
        request,
        "Solo se pueden reabrir sesiones cerradas.",
        level="warning"
    )

# =========================================================
# ADMIN DE CONTEO SESIÓN
# =========================================================
@admin.register(ConteoSesion)
class ConteoSesionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'tipo',
        'estado',
        'usuario',
        'fecha_creacion',
    )

    list_display_links = ('id', 'nombre')

    list_filter = ('estado', 'usuario', 'fecha_creacion')

    search_fields = ('nombre', 'id', 'usuario__username')

    ordering = ('-fecha_creacion',)

    inlines = [ConteoLineaInline]

    actions = [reabrir_conteo_admin]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'importar-xlsx/',
                self.admin_site.admin_view(self.importar_xlsx_view),
                name='importar_conteo_xlsx',
            ),
        ]
        return custom_urls + urls

    def importar_xlsx_view(self, request):
        if request.method == 'POST':
            archivo = request.FILES.get('archivo')
            if archivo:
                self.message_user(
                    request,
                    "Función de importación desactivada temporalmente."
                )
                return redirect("..")
        return render(request, "admin/importar_xlsx.html")

# =========================================================
# ADMIN DE PRODUCTO (CON IMPORT/EXPORT EXCEL)
# =========================================================
@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    resource_class = ProductoResource

    # ⭐ CLAVE PARA ACTIVAR SELECT2 Y EL AUTOCOMPLETADO
    autocomplete_fields = ['proveedor']

    list_display = (
        'nombre_interno',
        'codigo_interno',
        'categoria',
        'unidad_medida',
        'proveedor',
        'precio_compra',
        'stock_actual',
        'total_stock',
        'codigo_barras',
        'activo',
    )

    search_fields = (
        'nombre_interno',
        'codigo_interno',
        'codigo_barras',
        'nombre_proveedor',
    )

    def total_stock(self, obj):
        if obj.stock_actual is None or obj.precio_compra is None:
            return 0
        return round(obj.stock_actual * obj.precio_compra, 2)

    total_stock.short_description = "Total"

    # ← AÑADE ESTE BLOQUE AQUÍ
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            qs = response.context_data["cl"].queryset
            total_general = sum(
                (p.stock_actual or 0) * (p.precio_compra or 0)
                for p in qs
            )
            response.context_data["total_general"] = round(total_general, 2)
        except:
            pass

        return response

    # ⭐ CLAVE PARA ACTIVAR SELECT2 Y EL AUTOCOMPLETADO
    autocomplete_fields = ['proveedor'] # ← ESTA ES LA LÍNEA QUE FALTABA

    list_filter = (
        'categoria',
        'unidad_medida',
        'proveedor',
        'iva',
        'activo',
    )

    ordering = ('nombre_interno',)

    # =========================================================
    # AUTOCOMPLETAR CÓDIGO INTERNO AL CREAR PRODUCTO
    # =========================================================
    def get_changeform_initial_data(self, request):
        ultimo = Producto.objects.order_by("-id").first()
        if ultimo and ultimo.codigo_interno:
            try:
                nuevo = int(ultimo.codigo_interno) + 1
                return {"codigo_interno": str(nuevo)}
            except:
                pass
        return {"codigo_interno": "1"}

# =========================================================
# REGISTROS BÁSICOS
# =========================================================
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    list_display = ('nombre', 'telefono', 'email')
    ordering = ('nombre',)

@admin.register(IVA)
class IVAAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura')

# =========================================================
# ADMIN DE ASIENTOS CONTABLES (INVENTARIO)
# =========================================================
@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sesion_conteo',
        'tipo',
        'descripcion',
        'importe',
        'fecha',
        'usuario',
    )
    list_filter = ('tipo', 'fecha')
    search_fields = ('descripcion',)
