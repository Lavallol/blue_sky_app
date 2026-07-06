# inventario_app/servicios/servicio_escandallo.py

from produccion_app.models import Escandallo, EscandalloLinea


class ServicioEscandallo:
    """
    Servicio encargado de recalcular escandallos cuando cambia el coste
    de un producto ingrediente.
    """

    @staticmethod
    def recalcular_escandallos_por_producto(producto):
        """
        Recalcula todos los escandallos que utilizan este producto como ingrediente.
        Devuelve la lista de escandallos actualizados.
        """
        escandallos = Escandallo.objects.filter(
            lineas__producto=producto
        ).distinct()

        escandallos_actualizados = []

        for escandallo in escandallos:
            ServicioEscandallo.recalcular_escandallo(escandallo)
            escandallos_actualizados.append(escandallo)

        return escandallos_actualizados

    @staticmethod
    def recalcular_escandallo(escandallo):
        """
        Recalcula el coste total y el coste unitario del escandallo.
        """
        total_coste = 0

        for linea in escandallo.lineas.all():
            coste_linea = linea.producto.coste_actual * linea.cantidad
            total_coste += coste_linea

        escandallo.coste_total = total_coste

        # Evitar división por cero
        if escandallo.unidades_producidas > 0:
            escandallo.coste_unitario = total_coste / escandallo.unidades_producidas
        else:
            escandallo.coste_unitario = 0

        escandallo.save(update_fields=["coste_total", "coste_unitario"])

        return escandallo
