from typing import Union
from django.db import transaction
from inventario_app.models import Producto

# Intentamos importar MovimientoStock si existe
try:
    from inventario_app.models import MovimientoStock
    TIENE_MOVIMIENTO_STOCK = True
except Exception:
    MovimientoStock = None
    TIENE_MOVIMIENTO_STOCK = False


class ServicioActualizarStock:
    """
    Servicio aislado para ajustar stock sin tocar la lógica de conteo
    ni los modelos existentes.
    """

    @staticmethod
    @transaction.atomic
    def aplicar_ajuste(
        producto: Producto,
        diferencia: Union[int, float],
        motivo: str,
        referencia: str,
        usuario=None,
        sesion=None,
    ):
        """
        Ajusta el stock del producto y, si existe, registra un movimiento de stock.
        """
        stock_anterior = producto.stock_actual
        nuevo_stock = stock_anterior + diferencia

        producto.stock_actual = nuevo_stock
        producto.save(update_fields=["stock_actual"])

        if TIENE_MOVIMIENTO_STOCK:
            ServicioActualizarStock.registrar_movimiento(
                producto=producto,
                cantidad=diferencia,
                motivo=motivo,
                referencia=referencia,
                stock_anterior=stock_anterior,
                stock_nuevo=nuevo_stock,
                usuario=usuario,
                sesion=sesion,
            )

    @staticmethod
    def registrar_movimiento(
        producto: Producto,
        cantidad: Union[int, float],
        motivo: str,
        referencia: str,
        stock_anterior: Union[int, float],
        stock_nuevo: Union[int, float],
        usuario=None,
        sesion=None,
    ):
        """
        Registra un movimiento de stock si el modelo MovimientoStock existe.
        """
        if not TIENE_MOVIMIENTO_STOCK:
            return

        tipo = "ajuste_positivo" if cantidad > 0 else "ajuste_negativo"

        MovimientoStock.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=cantidad,
            stock_antes=stock_anterior,
            stock_despues=stock_nuevo,
            referencia=referencia,
            origen=motivo,
            usuario=usuario,
            sesion=sesion,
        )
