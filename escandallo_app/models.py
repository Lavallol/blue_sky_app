from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from inventario_app.models import Producto


class Escandallo(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    # Rendimiento en raciones / unidades finales
    rendimiento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Número de raciones o unidades que produce este escandallo."
    )

    # Precio de venta SIN IVA por ración / unidad
    precio_venta_sin_iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precio de venta sin IVA por ración/unidad."
    )

    class Meta:
        verbose_name = "Escandallo"
        verbose_name_plural = "Escandallos"

    def __str__(self):
        return self.nombre

    # ---- COSTES CALCULADOS ----

    @property
    def coste_total(self):
        """
        Suma del coste REAL de todas las líneas (ya con mermas aplicadas).
        """
        total = Decimal("0.00")
        for linea in self.lineas.all():
            total += linea.coste_real or Decimal("0.00")
        return total

    @property
    def coste_por_racion(self):
        """
        Coste por ración/unidad final.
        """
        if not self.rendimiento or self.rendimiento == 0:
            return None
        return (self.coste_total / self.rendimiento).quantize(Decimal("0.01"))

    @property
    def margen_unitario(self):
        """
        Margen absoluto por ración/unidad.
        """
        if self.precio_venta_sin_iva is None:
            return None
        if self.coste_por_racion is None:
            return None
        return (self.precio_venta_sin_iva - self.coste_por_racion).quantize(Decimal("0.01"))

    @property
    def porcentaje_coste(self):
        """
        Porcentaje de coste sobre el precio de venta.
        """
        if self.precio_venta_sin_iva in (None, 0):
            return None
        if self.coste_por_racion is None:
            return None
        return (self.coste_por_racion / self.precio_venta_sin_iva * 100).quantize(Decimal("0.01"))
    

class EscandalloLinea(models.Model):
    escandallo = models.ForeignKey(
        Escandallo,
        on_delete=models.CASCADE,
        related_name="lineas"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )

    # Cantidad BRUTA (antes de merma)
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.000"))],
        help_text="Cantidad BRUTA utilizada (antes de merma)."
    )

    unidad = models.CharField(
        max_length=20,
        default="g",
        help_text="Unidad de medida (g, kg, ml, l, ud, etc.)."
    )

    # Merma en porcentaje (0–100)
    merma_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        help_text="Porcentaje de merma de este ingrediente."
    )

    # Precio de coste unitario (se toma del producto en el momento del escandallo)
    precio_coste = models.DecimalField(
        max_digits=10,
        decimal_places=2,   # ← CAMBIADO A 2 DECIMALES
        blank=True,         # ← PERMITE AUTOCOMPLETADO SIN ERROR
        help_text="Precio de coste unitario del producto en el momento del escandallo."
    )

    class Meta:
        verbose_name = "Línea de escandallo"
        verbose_name_plural = "Líneas de escandallo"

    def __str__(self):
        return f"{self.escandallo.nombre} — {self.producto.nombre_interno}"

    # ---- CÁLCULOS DE MERMAS Y COSTES ----

    @property
    def cantidad_neta(self):
        """
        Cantidad útil después de aplicar la merma.
        Blindado para evitar errores con datos antiguos.
        """
        if not self.cantidad:
            return Decimal("0.000")

        merma = self.merma_porcentaje or Decimal("0.00")
        factor = (Decimal("100.00") - merma) / Decimal("100.00")

        return (self.cantidad * factor).quantize(Decimal("0.000"))

    @property
    def coste_teorico(self):
        """
        Coste teórico sin considerar merma (cantidad BRUTA × precio_coste).
        """
        if self.precio_coste is None or not self.cantidad:
            return None
        return (self.cantidad * self.precio_coste).quantize(Decimal("0.0001"))

    @property
    def coste_real(self):
        """
        Coste real considerando merma (cantidad NETA × precio_coste).
        """
        if self.precio_coste is None:
            return None
        return (self.cantidad_neta * self.precio_coste).quantize(Decimal("0.0001"))

    def cargar_precio_desde_producto(self):
        """
        Carga el precio de coste desde el producto según su método de valoración.
        No toca inventario ni compras: solo lee.
        """
        if hasattr(self.producto, "get_costo_actual"):
            self.precio_coste = self.producto.get_costo_actual()
        else:
            self.precio_coste = self.producto.precio_compra

    def save(self, *args, **kwargs):
        # Autocompletar SIEMPRE el precio desde el producto
        self.cargar_precio_desde_producto()
        super().save(*args, **kwargs)
