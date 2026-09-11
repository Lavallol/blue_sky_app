# ============================================================
#   MODELO INTERMEDIO REAL — MEFIE
#   Conecta FacturaCompra ↔ AlbaranCompraLinea
# ============================================================

from django.db import models
from .factura import FacturaCompra
from .albaran import AlbaranCompraLinea

class FacturaCompraAlbaranLinea(models.Model):
    factura = models.ForeignKey(
        FacturaCompra,
        on_delete=models.CASCADE,
        related_name="albaran_lineas_factura"
    )

    albaran_linea = models.ForeignKey(
        AlbaranCompraLinea,
        on_delete=models.PROTECT,
        related_name="facturas_asociadas"
    )

    # Campos industriales MEFIE
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    importe_iva = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Línea de Albarán en Factura"
        verbose_name_plural = "Líneas de Albarán en Factura"

    def __str__(self):
        return f"Línea {self.albaran_linea.id} en Factura {self.factura.id}"
