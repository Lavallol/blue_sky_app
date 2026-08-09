from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from inventario_app.models import Producto

def api_producto_pedido(request, producto_id):
    """
    Devuelve precio e IVA del producto para autocompletar
    líneas del PedidoCompra.
    """

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)

    return JsonResponse({
        "id": producto.id,
        "nombre": producto.nombre_interno,
        "precio": float(producto.precio_compra or 0),
        "iva": float(producto.iva.porcentaje if producto.iva else 0),
    })
