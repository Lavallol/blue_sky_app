rom inventario_app.models import Producto, MovimientoStock
from django.db import transaction

class ServicioStock:

    @staticmethod
    @transaction.atomic
    def incrementar_stock(producto: Producto, cantidad: float, origen: str):
        nuevo_stock = producto.stock_actual + cantidad
        ServicioStock._actualizar_producto(producto, nuevo_stock)
        ServicioStock._registrar_movimiento(producto, cantidad, "ENTRADA", origen)

    @staticmethod
    @transaction.atomic
    def disminuir_stock(producto: Producto, cantidad: float, origen: str):
        nuevo_stock = producto.stock_actual - cantidad
        ServicioStock._actualizar_producto(producto, nuevo_stock)
        ServicioStock._registrar_movimiento(producto, -cantidad, "SALIDA", origen)

    @staticmethod
    @transaction.atomic
    def ajustar_stock(producto: Producto, cantidad_final: float, origen: str):
        diferencia = cantidad_final - producto.stock_actual
        ServicioStock._actualizar_producto(producto, cantidad_final)
        ServicioStock._registrar_movimiento(producto, diferencia, "AJUSTE", origen)

    @staticmethod
    def _actualizar_producto(producto: Producto, nuevo_stock: float):
        producto.stock_actual = nuevo_stock
        producto.save()

    @staticmethod
    def _registrar_movimiento(producto: Producto, cantidad: float, origen: str, usuario):
        stock_antes = producto.stock_actual
        stock_despues = producto.stock_actual + cantidad

        MovimientoStock.objects.create(
            producto=producto,
            stock_antes=stock_antes,
            stock_despues=stock_despues,
            diferencia=cantidad,
            usuario=usuario,
            origen=origen
    )
