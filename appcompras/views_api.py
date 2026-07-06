from django.http import JsonResponse
from inventario_app.models import Producto

def api_producto_info(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)

        return JsonResponse({
            "precio": float(producto.precio_compra or 0),
            "iva": float(producto.iva.porcentaje) if producto.iva else 0,
        })

    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
