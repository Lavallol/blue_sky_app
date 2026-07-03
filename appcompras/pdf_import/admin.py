from django.contrib import admin
from .models import DocumentoPDFImportado, LineaPDFImportada, PlantillaProveedor, HistorialPDF


@admin.register(DocumentoPDFImportado)
class DocumentoPDFImportadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_documento', 'numero_documento', 'proveedor_detectado', 'estado', 'fecha_importacion')
    list_filter = ('estado', 'tipo_documento', 'proveedor_detectado')
    search_fields = ('numero_documento', 'errores_detectados')


@admin.register(LineaPDFImportada)
class LineaPDFImportadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'documento', 'producto_detectado', 'descripcion', 'cantidad', 'precio_unitario', 'estado')
    list_filter = ('estado',)
    search_fields = ('descripcion', 'referencia_proveedor')


@admin.register(PlantillaProveedor)
class PlantillaProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'nombre', 'version', 'activo', 'fecha_actualizacion')
    list_filter = ('activo',)
    search_fields = ('proveedor__nombre', 'nombre')


@admin.register(HistorialPDF)
class HistorialPDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'documento', 'accion', 'fecha', 'usuario')
    list_filter = ('accion', 'fecha')
    search_fields = ('detalle',)
