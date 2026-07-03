# inventario_app/services/actualizar_stock.py

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
            )

    @staticmethod
    def registrar_movimiento(
        producto: Producto,
        cantidad: Union[int, float],
        motivo: str,
        referencia: str,
        stock_anterior: Union[int, float],
        stock_nuevo: Union[int, float],
    ):
        """
        Registra un movimiento de stock si el modelo MovimientoStock existe.
        """
        if not TIENE_MOVIMIENTO_STOCK:
            return

        MovimientoStock.objects.create(
            producto=producto,
            cantidad=cantidad,
            motivo=motivo,
            referencia=referencia,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
        )
