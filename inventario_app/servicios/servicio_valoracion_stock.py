from inventario_app.models import Producto

class ServicioValoracionStock:
    """
    Actualiza el coste del producto recibido según el método de valoración:
    - Último Coste
    - Coste Medio
    """

    def actualizar_coste(self, producto, cantidad, coste_unitario):
        metodo = producto.metodo_valoracion

        # ================================
        # MÉTODO 1: ÚLTIMO COSTE
        # ================================
        if metodo == Producto.METODO_ULTIMO_COSTE:
            # Actualizamos el precio de compra directamente
            producto.precio_compra = coste_unitario
            producto.save(update_fields=["precio_compra"])
            return producto

        # ================================
        # MÉTODO 2: COSTE MEDIO PONDERADO
        # ================================
        elif metodo == Producto.METODO_COSTE_MEDIO:
            stock_anterior = producto.stock_actual - cantidad

            if stock_anterior < 0:
                stock_anterior = 0  # seguridad

            coste_anterior = producto.precio_compra

            # Fórmula de coste medio ponderado
            nuevo_coste = (
                (stock_anterior * coste_anterior) + (cantidad * coste_unitario)
            ) / (stock_anterior + cantidad)

            producto.precio_compra = nuevo_coste
            producto.save(update_fields=["precio_compra"])
            return producto

        # ================================
        # ERROR SI EL MÉTODO NO EXISTE
        # ================================
        else:
            raise ValueError(f"Método de valoración desconocido: {metodo}")
