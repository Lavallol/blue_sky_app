from django.db import models
from inventario_app.models import Producto
from escandallo_app.models import Escandallo

# ---------------------------------------------------------
# PRODUCCIÓN
# ---------------------------------------------------------

class Produccion(models.Model):
    escandallo = models.ForeignKey(
        Escandallo,
        on_delete=models.PROTECT,
        related_name='producciones'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=100, blank=True, null=True)
    rendimiento_real = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Producción"
        verbose_name_plural = "Producciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"Producción de {self.escandallo.nombre} ({self.fecha.date()})"


# ---------------------------------------------------------
# LÍNEAS DE PRODUCCIÓN
# ---------------------------------------------------------

class ProduccionLinea(models.Model):
    produccion = models.ForeignKey(
        Produccion,
        on_delete=models.CASCADE,
        related_name='lineas'
    )
    ingrediente = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )
    cantidad_real = models.DecimalField(max_digits=10, decimal_places=3)
    unidad = models.CharField(max_length=20, default="g")
    merma = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    # Campo necesario para PASO 8.1
    cantidad_teorica = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    class Meta:
        verbose_name = "Línea de producción"
        verbose_name_plural = "Líneas de producción"

    def __str__(self):
        return f"{self.ingrediente.nombre_interno} ({self.cantidad_real}{self.unidad})"