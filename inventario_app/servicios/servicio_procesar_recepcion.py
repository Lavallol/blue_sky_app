# inventario_app/servicios/servicio_procesar_recepcion.py

from inventario_app.servicios.servicio_confirmacion import ServicioConfirmacionRecepcion
from inventario_app.servicios.servicio_valoracion_stock import ServicioValoracionStock

# ⚠️ Módulos de producción desactivados temporalmente
# from inventario_app.servicios.servicio_escandallo import ServicioEscandallo
# from inventario_app.servicios.servicio_valoracion_producto_final import ServicioValoracionProductoFinal


class ServicioProcesarRecepcion:
    """
    Orquesta el flujo de recepción de compras:
    1) Confirma recepción y actualiza stock físico.
    2) Actualiza el coste del producto.
    (Escandallos y productos finales desactivados hasta que exista produccion_app)
    """

    @staticmethod
    def procesar_linea_albaran(linea_albaran):

        # 1) Confirmar recepción y actualizar stock físico
        servicio_confirmacion = ServicioConfirmacionRecepcion()
        producto, cantidad, coste_unitario = servicio_confirmacion.confirmar(linea_albaran)

        # 2) Actualizar valoración de stock del producto
        servicio_valoracion = ServicioValoracionStock()
        producto_valorado = servicio_valoracion.actualizar_coste(
            producto=producto,
            cantidad=cantidad,
            coste_unitario=coste_unitario,
        )

        # 3) Escandallos desactivados temporalmente
        escandallos_actualizados = []
        productos_finales_actualizados = []

        return {
            "producto": producto_valorado,
            "escandallos_actualizados": escandallos_actualizados,
            "productos_finales_actualizados": productos_finales_actualizados,
        }
