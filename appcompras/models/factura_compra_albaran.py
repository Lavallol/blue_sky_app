from django.db import models
from .factura import FacturaCompra
from .albaran import AlbaranCompra


class FacturaCompraAlbaran(models.Model):
    factura = models.ForeignKey(FacturaCompra, on_delete=models.CASCADE, related_name='factura_albaranes')
    albaran = models.ForeignKey(AlbaranCompra, on_delete=models.CASCADE, related_name='albaran_facturas')

    class Meta:
        unique_together = ('factura', 'albaran')
        verbose_name = "Factura - Albarán"
        verbose_name_plural = "Facturas - Albaranes"

    def __str__(self):
        return f"{self.factura} ↔ {self.albaran}"
