from django.db import models
from inventario_app.models import Proveedor, Producto
from .pedido import PedidoCompra


class AlbaranCompra(models.Model):
    ESTADOS_ALBARAN = [
        ('BORRADOR', 'Borrador'),
        ('CONFIRMADO', 'Confirmado'),
        ('FACTURADO', 'Facturado'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)

    pedido = models.ForeignKey(
        PedidoCompra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='albaranes'
    )

    fecha_recepcion = models.DateField()
    numero_albaran = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_ALBARAN, default='BORRADOR')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ============================================================
    #  🔧 CAMBIO IMPORTANTE:
    #  related_name='albaranes_directos' para evitar choque con
    #  FacturaCompra.albaranes (ManyToMany)
    # ============================================================
    factura = models.ForeignKey(
        'FacturaCompra',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='albaranes_directos'
    )

    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("puede_reabrir_albaranes_compra", "Puede reabrir albaranes de compra"),
        ]

    def __str__(self):
        return f"Albarán {self.numero_albaran or self.id} - {self.proveedor.nombre}"

    # ---------------------------
    # CÁLCULO PROFESIONAL DE TOTALES
    # ---------------------------
    def recalcular_totales(self):
        lineas = self.lineas.all()

        subtotal = 0
        iva_total = 0

        for linea in lineas:
            subtotal += float(linea.total_linea)
            iva_total += float(linea.total_linea) * (float(linea.iva) / 100)

        self.subtotal = subtotal
        self.iva_total = iva_total
        self.total = subtotal + iva_total

        self.save(update_fields=["subtotal", "iva_total", "total"])


class AlbaranCompraLinea(models.Model):
    albaran = models.ForeignKey(
        AlbaranCompra,
        on_delete=models.CASCADE,
        related_name='lineas'
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_linea = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    total_linea = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    devuelto = models.BooleanField(default=False)
    motivo_devolucion = models.CharField(max_length=200, blank=True, null=True)

    @property
    def subtotal(self):
        cantidad = self.cantidad_recibida or 0
        precio = self.precio_unitario or 0
        descuento = self.descuento_linea or 0
        return (cantidad * precio) - descuento

    @property
    def importe_iva(self):
        iva = self.iva or 0
        return self.subtotal * (iva / 100)

    @property
    def total_linea_con_iva(self):
        iva = self.iva or 0
        return self.subtotal * (1 + iva / 100)


    def __str__(self):
        return f"{self.producto.nombre_interno} x {self.cantidad_recibida}"

    # ---------------------------
    # STOCK ANTES / DESPUÉS
    # ---------------------------
    def stock_antes(self):
        if not self.producto_id:
            return None
        return self.producto.stock_actual

    def stock_despues(self):
        if not self.producto_id:
            return None
        if self.cantidad_recibida is None:
            return self.stock_antes()
        return self.stock_antes() + self.cantidad_recibida

    stock_antes.short_description = "Stock antes"
    stock_despues.short_description = "Stock después"

    # ---------------------------
    # AUTOCOMPLETADO + TOTALES AUTOMÁTICOS
    # ---------------------------
    def save(self, *args, **kwargs):

        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_compra

        if self.producto.iva:
            self.iva = self.producto.iva.porcentaje

        precio_desc = self.precio_unitario * (1 - (self.descuento_linea / 100))
        self.total_linea = precio_desc * self.cantidad_recibida

        super().save(*args, **kwargs)

        self.albaran.recalcular_totales()
