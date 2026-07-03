from django.shortcuts import render, get_object_or_404
from .models import ConteoSesion, ConteoLinea, Producto

def conteo_codigo_barras(request, sesion_id):
    """
    Vista principal del módulo de conteo.
    Carga la sesión y sus líneas, y renderiza el template correcto.
    """

    # Obtener la sesión
    sesion = get_object_or_404(ConteoSesion, id=sesion_id)

    # Obtener las líneas de esa sesión
    lineas = ConteoLinea.objects.filter(sesion=sesion).select_related("producto")

    # Renderizar el template correcto
    return render(request, "inventario/conteo_codigo_barras.html", {
        "sesion": sesion,
        "lineas": lineas,
    })
