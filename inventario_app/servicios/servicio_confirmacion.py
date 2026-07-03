from inventario_app.models import Producto, MovimientoStock

class ServicioConfirmacionRecepcion:
    """
    Confirma la recepción de un albarán y actualiza el stock físico
    registrando un movimiento profesional de inventario.
    """

    def confirmar(self, linea_albaran):
        producto = linea_albaran.producto

        # ✔ CORREGIDO: usar cantidad_recibida
        cantidad = linea_albaran.cantidad_recibida

        # ✔ CORREGIDO: usar precio_unitario
        coste_unitario = linea_albaran.precio_unitario

        # Registrar movimiento de stock profesional
        MovimientoStock.registrar(
            producto=producto,
            cantidad=cantidad,  # cantidad positiva = entrada
            tipo="entrada",
            referencia=f"Albarán {linea_albaran.albaran.id}",
            origen="compras",
            usuario=None,  # tu modelo Albarán no tiene usuario
            coste_unitario=coste_unitario,
        )

        # Devolver datos para el siguiente servicio (valoración)
        return producto, cantidad, coste_unitario
