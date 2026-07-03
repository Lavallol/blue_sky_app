from django.db import models

class CondicionPago(models.Model):
    nombre = models.CharField(max_length=50)  # Contado, 7 días, 15 días, 30 días...
    dias = models.PositiveIntegerField(default=0)  # Días hasta el vencimiento
    descuento_pronto_pago = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # %
    dias_pronto_pago = models.PositiveIntegerField(default=0)  # Días para aplicar pronto pago
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
