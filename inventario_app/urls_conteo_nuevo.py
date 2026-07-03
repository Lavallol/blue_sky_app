from django.urls import path
from . import views_conteo_nuevo as views

urlpatterns = [
    # Página principal del módulo
    path("", views.conteo_index, name="conteo_index"),

    # Crear nueva sesión
    path("nueva/", views.nueva_sesion, name="conteo_nueva"),

    # Cargar sesión existente
    path("sesion/<int:sesion_id>/", views.sesion_conteo, name="conteo_sesion"),

    # Resumen de sesión
    path("resumen/<int:sesion_id>/", views.resumen_sesion, name="resumen_sesion"),

    # APIs AJAX (corregidas)
    path("api/buscar_producto/", views.api_buscar_producto, name="api_buscar_producto"),
    path("api/agregar_linea/", views.api_agregar_linea, name="api_agregar_linea"),
    path("api/actualizar_linea/", views.api_actualizar_linea, name="api_actualizar_linea"),
    path("api/eliminar_linea/", views.api_eliminar_linea, name="api_eliminar_linea"),

    # Acciones de sesión
    path("cerrar/<int:sesion_id>/", views.cerrar_sesion, name="cerrar_sesion"),
    path("reabrir/<int:sesion_id>/", views.reabrir_sesion, name="reabrir_sesion"),
    path("aplicar/<int:sesion_id>/", views.aplicar_diferencias, name="aplicar_diferencias"),

    # Exportaciones
    path("exportar_excel/<int:sesion_id>/", views.exportar_excel_conteo, name="exportar_excel_conteo"),
    path("exportar_pdf/<int:sesion_id>/", views.exportar_pdf_conteo, name="exportar_pdf_conteo"),
]
