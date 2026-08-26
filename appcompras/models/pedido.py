from django.db import models
from inventario_app.models import Proveedor, Producto
from decimal import Decimal


class PedidoCompra(models.Model):

    # -----------------------------
    # ESTADOS DEL PEDIDO
    # -----------------------------
    BORRADOR = 'BORRADOR'
    CONFIRMADO = 'CONFIRMADO'
    PARCIAL = 'PARCIALMENTE_RECIBIDO'
    CERRADO = 'CERRADO'
    CANCELADO = 'CANCELADO'

    ESTADOS_PEDIDO = [
        (BORRADOR, 'Borrador'),
        (CONFIRMADO, 'Confirmado'),
        (PARCIAL, 'Parcialmente recibido'),
        (CERRADO, 'Cerrado'),
        (CANCELADO, 'Cancelado'),
    ]

    # -----------------------------
    # CAMPOS PRINCIPALES
    # -----------------------------
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha_pedido = models.DateField()
    fecha_prevista = models.DateField(blank=True, null=True)

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS_PEDIDO,
        default=BORRADOR
    )

    # -----------------------------
    # TOTALES DEL PEDIDO
    # -----------------------------
    subtotal_antes_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento_global = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    importe_descuento_global = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"Pedido {self.id} - {self.proveedor.nombre}"

    # -----------------------------
    # CÁLCULO AUTOMÁTICO DE TOTALES
    # -----------------------------
    def recalcular_totales(self):
        lineas = self.lineas.all()

        self.subtotal_antes_descuento = sum(
            (l.cantidad_pedida * l.precio_unitario) for l in lineas
        )

        self.importe_descuento_global = (
            self.subtotal_antes_descuento * (self.descuento_global / 100)
        )

        self.subtotal = self.subtotal_antes_descuento - self.importe_descuento_global

        self.iva_total = sum(l.iva_importe for l in lineas)

        self.total = self.subtotal + self.iva_total

        self.save(update_fields=[
            "subtotal_antes_descuento",
            "importe_descuento_global",
            "subtotal",
            "iva_total",
            "total"
        ])

    # -----------------------------
    # ACTUALIZACIÓN DE ESTADO SEGÚN RECEPCIONES
    # -----------------------------
    def actualizar_estado_por_recepciones(self):
        lineas = self.lineas.all()

        if all(l.cantidad_pendiente == 0 for l in lineas):
            self.estado = self.CERRADO
        elif any(l.cantidad_recibida > 0 for l in lineas):
            self.estado = self.PARCIAL

        self.save(update_fields=["estado"])


class PedidoCompraLinea(models.Model):

    # -----------------------------
    # ESTADOS DE LÍNEA
    # -----------------------------
    BORRADOR = 'BORRADOR'
    CONFIRMADA = 'CONFIRMADA'
    PARCIAL = 'PARCIAL'
    COMPLETA = 'COMPLETA'

    ESTADOS_LINEA = [
        (BORRADOR, 'Borrador'),
        (CONFIRMADA, 'Confirmada'),
        (PARCIAL, 'Parcial'),
        (COMPLETA, 'Completa'),
    ]

    pedido = models.ForeignKey(
        PedidoCompra,
        on_delete=models.CASCADE,
        related_name='lineas'
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    # -----------------------------
    # CANTIDADES
    # -----------------------------
    cantidad_pedida = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def cantidad_pendiente(self):
        return max(self.cantidad_pedida - self.cantidad_recibida, 0)

    # -----------------------------
    # PRECIOS Y TOTALES
    # -----------------------------
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_linea = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # IVA real del producto (puede ser 0, 5, 10, 21…)
    iva = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva_importe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_linea = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado_linea = models.CharField(
        max_length=20,
        choices=ESTADOS_LINEA,
        default=BORRADOR
    )

    # -----------------------------
    # ✔ usar nombre_interno
    # -----------------------------
    def __str__(self):
        return f"{self.producto.nombre_interno} x {self.cantidad_pedida}"

    # -----------------------------
    # AUTOCOMPLETADO + CÁLCULO AUTOMÁTICO
    # -----------------------------
    def save(self, *args, **kwargs):

        if self.producto and (self.precio_unitario is None or self.precio_unitario == 0):
            self.precio_unitario = self.producto.precio_compra

        # 1) Tomar SIEMPRE el IVA del producto (aunque sea 0%)
        if self.producto.iva is not None:
            self.iva = self.producto.iva.porcentaje

        # 2) Blindaje: si el admin envía IVA vacío ('') → Django lo convierte en None
        if self.iva is None:
            self.iva = self.producto.iva.porcentaje if self.producto.iva is not None else 0

        # 3) Convertir IVA a Decimal para evitar errores Decimal × float
        self.iva = Decimal(str(self.iva))

        base = self.cantidad_pedida * self.precio_unitario
        desc = base * (self.descuento_linea / 100)
        self.subtotal = base - desc

        self.iva_importe = self.subtotal * (self.iva / Decimal('100'))
        self.total_linea = self.subtotal + self.iva_importe

        super().save(*args, **kwargs)

        self.pedido.recalcular_totales()
