from django.urls import path

# Vistas antiguas (productos)
from . import views

# Vistas nuevas del módulo de conteo profesional
from . import views_conteo_nuevo as conteo


urlpatterns = [

    # ---------------------------------------------------------
    # PRODUCTOS
    # ---------------------------------------------------------
    path("productos/", views.lista_productos, name="lista_productos"),
    path("productos/crear/", views.crear_producto, name="crear_producto"),
    path("productos/exportar/xlsx/", views.exportar_productos_xlsx, name="exportar_productos_xlsx"),
    path("productos/exportar/pdf/", views.exportar_productos_pdf, name="exportar_productos_pdf"),

    # ---------------------------------------------------------
    # CONTEO PROFESIONAL (nuevo módulo)
    # ---------------------------------------------------------

    # Página principal del módulo
    path("conteo/", conteo.conteo_index, name="conteo_index"),

    # Crear nueva sesión
    path("conteo/nueva/", conteo.nueva_sesion, name="nueva_sesion"),

    # Cargar sesión
    path("conteo/sesion/<int:sesion_id>/", conteo.sesion_conteo, name="sesion_conteo"),

    # Resumen profesional
    path("conteo/resumen/<int:sesion_id>/", conteo.resumen_sesion, name="resumen_sesion"),

    # Cerrar / Reabrir / Aplicar diferencias
    path("conteo/cerrar/<int:sesion_id>/", conteo.cerrar_sesion, name="cerrar_sesion"),
    path("conteo/reabrir/<int:sesion_id>/", conteo.reabrir_sesion, name="reabrir_sesion"),
    path("conteo/aplicar/<int:sesion_id>/", conteo.aplicar_diferencias, name="aplicar_diferencias"),

    # ---------------------------------------------------------
    # API (AJAX)
    # ---------------------------------------------------------
    path("conteo/api/buscar/", conteo.api_buscar_producto, name="api_buscar_producto"),
    path("conteo/api/agregar_linea/", conteo.api_agregar_linea, name="api_agregar_linea"),
    path("conteo/api/actualizar_linea/", conteo.api_actualizar_linea, name="api_actualizar_linea"),
    path("conteo/api/eliminar_linea/", conteo.api_eliminar_linea, name="api_eliminar_linea"),

    # ---------------------------------------------------------
    # EXPORTACIONES PROFESIONALES
    # ---------------------------------------------------------
    path("conteo/exportar_pdf/<int:sesion_id>/", conteo.exportar_pdf_conteo, name="exportar_pdf_conteo"),
    path("conteo/exportar_excel/<int:sesion_id>/", conteo.exportar_excel_conteo, name="exportar_excel_conteo"),

    # ---------------------------------------------------------
    # IMPORTACIÓN PROFESIONAL DESDE EXCEL (CORREGIDO)
    # ---------------------------------------------------------
    path("conteo/importar_excel/<int:sesion_id>/", conteo.importar_excel_conteo, name="importar_excel_conteo"),
]
