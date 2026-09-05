from django.db import models
from inventario_app.models import Proveedor, Producto
from .condicion_pago import CondicionPago
from appcompras.models.albaran import AlbaranCompra


class FacturaCompra(models.Model):
    ESTADOS_FACTURA = [
        ('BORRADOR', 'Borrador'),
        ('CONTABILIZADA', 'Contabilizada'),
        ('ANULADA', 'Anulada'),
    ]

    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente'),
        ('PARCIAL', 'Parcialmente pagada'),
        ('PAGADA', 'Pagada'),
        ('VENCIDA', 'Vencida'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha_factura = models.DateField()
    numero_factura = models.CharField(max_length=50)

    # ⭐ CORRECCIÓN PROFESIONAL: HACER OPCIONAL EL CAMPO
    condicion_pago = models.ForeignKey(
        CondicionPago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )

    descuento_global = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    importe_descuento_global = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    importe_subtotal = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    importe_impuestos = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    estado_factura = models.CharField(max_length=20, choices=ESTADOS_FACTURA, default='BORRADOR')
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE')

    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ============================================================
    #   RELACIÓN PROFESIONAL PARA OCR Y FACTURAS AGRUPADAS
    # ============================================================
    albaranes = models.ManyToManyField(
        AlbaranCompra,
        related_name="facturas_asociadas",
        blank=True
    )

    class Meta:
        permissions = [
            ("puede_anular_facturas_compra", "Puede anular facturas de compra"),
        ]

    # ⭐⭐⭐ CAMBIO SEGURO: __str__ A PRUEBA DE FALLOS ⭐⭐⭐
    def __str__(self):
        proveedor = self.proveedor.nombre if self.proveedor else "Sin proveedor"
        return f"{self.numero_factura} - {proveedor}"

    # ============================================================
    #   ASIGNAR CONDICIÓN DE PAGO AUTOMÁTICA DESDE EL PROVEEDOR
    # ============================================================
    def save(self, *args, **kwargs):
        # ⭐ SEGURO: autocompletar solo si está vacío
        if not getattr(self, "condicion_pago_id", None) and self.proveedor:
            if hasattr(self.proveedor, "condicion_pago") and self.proveedor.condicion_pago:
                self.condicion_pago = self.proveedor.condicion_pago

        super().save(*args, **kwargs)

    # ============================================================
    #   CÁLCULO AUTOMÁTICO DE TOTALES DE FACTURA
    # ============================================================
    def recalcular_totales(self):
        lineas = self.lineas.all()

        subtotal = 0
        impuestos = 0

        for l in lineas:
            base = (l.cantidad * l.precio_unitario) - l.importe_descuento
            subtotal += base
            impuestos += l.importe_impuestos

        self.importe_descuento_global = subtotal * (self.descuento_global / 100)
        self.importe_subtotal = subtotal - self.importe_descuento_global
        self.importe_impuestos = impuestos
        self.total = self.importe_subtotal + self.importe_impuestos

        self.save(update_fields=[
            "importe_descuento_global",
            "importe_subtotal",
            "importe_impuestos",
            "total",
        ])


class FacturaCompraLinea(models.Model):
    factura = models.ForeignKey(FacturaCompra, on_delete=models.CASCADE, related_name='lineas')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    importe_descuento = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # ============================================================
    #   NUEVO CAMPO IVA (igual que en Pedido y Albarán)
    # ============================================================
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=21)

    importe_impuestos = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.producto.nombre_interno} x {self.cantidad}"

    # ============================================================
    #   AUTOCOMPLETADO + CÁLCULO AUTOMÁTICO DE LÍNEA
    # ============================================================
    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_compra

        if self.producto.iva:
            self.iva = self.producto.iva.porcentaje

        base = (self.cantidad * self.precio_unitario) - self.importe_descuento
        self.importe_impuestos = base * (self.iva / 100)
        self.total = base + self.importe_impuestos

        super().save(*args, **kwargs)

        self.factura.recalcular_totales()

# ============================================================
#   MODELO INTERMEDIO MEFIE: Factura ↔ Albarán
# ============================================================

class FacturaCompraAlbaran(models.Model):
    factura = models.ForeignKey(FacturaCompra, on_delete=models.CASCADE)
    albaran = models.ForeignKey(AlbaranCompra, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('factura', 'albaran')
        verbose_name = "Albarán asociado"
        verbose_name_plural = "Albaranes asociados"

    def __str__(self):
        return f"{self.factura.numero_factura} ↔ {self.albaran.numero_albaran}"








