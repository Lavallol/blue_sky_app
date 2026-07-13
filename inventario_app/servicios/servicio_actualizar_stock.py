from inventario_app.models import MovimientoStock

class ServicioActualizarStock:

    @staticmethod
    def aplicar_ajuste(producto, diferencia, motivo, referencia, usuario=None):

        stock_antes = producto.stock_actual
        stock_despues = stock_antes + diferencia

        tipo = "ajuste_positivo" if diferencia > 0 else "ajuste_negativo"

        MovimientoStock.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=diferencia,
            stock_antes=stock_antes,
            stock_despues=stock_despues,
            referencia=referencia,
            origen=motivo,
            usuario=usuario,
        )

        producto.stock_actual = stock_despues
        producto.save(update_fields=["stock_actual"])
