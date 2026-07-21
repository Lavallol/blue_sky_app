class ServicioStock:

    @staticmethod
    def revertir_stock(producto, cantidad, origen):
        producto.stock_actual -= cantidad
        producto.save()

        # Movimiento inverso
        producto.registrar(
            cantidad=-cantidad,
            tipo="ajuste",
            referencia=origen,
            origen="reversion",
            usuario=None,
            coste_unitario=producto.valor_unitario,
        )
