# inventario_app/servicios/servicio_valoracion_producto_final.py

from produccion_app.models import Escandallo


class ServicioValoracionProductoFinal:
    """
    Actualiza el coste del producto final basándose en el coste del escandallo.
    Este servicio no toca ingredientes ni stock, solo el producto final.
    """

    @staticmethod
    def actualizar_coste_producto_final(escandallo):
        """
        Actualiza un único producto final a partir del escandallo recibido.
        Mantiene compatibilidad con tu implementación original.
        """
        producto_final = escandallo.producto_final
        producto_final.coste_actual = escandallo.coste_unitario
        producto_final.save(update_fields=["coste_actual"])
        return producto_final

    @staticmethod
    def actualizar_coste_productos_finales(escandallos):
        """
        Recibe una lista de escandallos ya recalculados y actualiza
        el coste_actual de todos los productos finales asociados.

        Devuelve la lista de productos finales actualizados.
        """
        productos_actualizados = []

        for escandallo in escandallos:
            producto_final = escandallo.producto_final
            producto_final.coste_actual = escandallo.coste_unitario
            producto_final.save(update_fields=["coste_actual"])
            productos_actualizados.append(producto_final)

        return productos_actualizados
