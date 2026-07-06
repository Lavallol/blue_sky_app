from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

# =========================================================
# FUNCIÓN PARA GENERAR CÓDIGO INTERNO AUTOMÁTICO
# =========================================================

def generar_codigo_interno():
    ultimo = Producto.objects.order_by('-codigo_interno').first()
    if ultimo and str(ultimo.codigo_interno).isdigit():
        return str(int(ultimo.codigo_interno) + 1)
    return "1"


# =========================================================
# MODELOS BÁSICOS
# =========================================================

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50)
    abreviatura = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"

    def __str__(self):
        return self.abreviatura


# =========================================================
# PROVEEDOR (VERSIÓN PROFESIONAL)
# =========================================================

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    cif = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    persona_contacto = models.CharField(max_length=150, blank=True, null=True)
    forma_pago = models.CharField(max_length=100, blank=True, null=True)
    plazo_pago = models.CharField(max_length=100, blank=True, null=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    referencia_interna = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre


class IVA(models.Model):
    nombre = models.CharField(max_length=50)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "IVA"
        verbose_name_plural = "IVA"

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje}%)"


# =========================================================
# PRODUCTO
# =========================================================

class Producto(models.Model):
    codigo_interno = models.CharField(max_length=50, unique=True)
    nombre_interno = models.CharField(max_length=150)
    nombre_proveedor = models.CharField(max_length=150, blank=True, null=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    iva = models.ForeignKey(IVA, on_delete=models.SET_NULL, null=True, blank=True)

    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_barras = models.CharField(max_length=50, unique=True, null=True, blank=True)

    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre_interno

    def save(self, *args, **kwargs):
        if not self.codigo_interno:
            self.codigo_interno = generar_codigo_interno()
        super().save(*args, **kwargs)

    def clean(self):
        errors = {}

        if self.stock_actual < 0:
            errors['stock_actual'] = "El stock actual no puede ser negativo."

        if self.stock_minimo < 0:
            errors['stock_minimo'] = "El stock mínimo no puede ser negativo."

        if self.precio_compra is None or self.precio_compra <= 0:
            errors['precio_compra'] = "El precio de compra debe ser mayor que cero."

        if not self.unidad_medida:
            errors['unidad_medida'] = "Debe seleccionar una unidad de medida."

        if self.codigo_barras:
            if Producto.objects.exclude(pk=self.pk).filter(codigo_barras=self.codigo_barras).exists():
                errors['codigo_barras'] = "Este código de barras ya está registrado en otro producto."

        if errors:
            raise ValidationError(errors)


# =========================================================
# CONTEO (SESIÓN + LÍNEAS)
# =========================================================

class ConteoSesion(models.Model):
    TIPOS = [
        ('conteo', 'Conteo'),
        ('revision', 'Revisión'),
        ('auditoria', 'Auditoría'),
    ]

    ESTADOS = [
        ('abierta', 'Abierta'),
        ('en_revision', 'En revisión'),
        ('cerrada', 'Cerrada'),
        ('aprobada', 'Aprobada'),
        ('aplicada', 'Aplicada'),
        ('reabierta', 'Reabierta'),
    ]

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='conteo')

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Evitar colisión con inventario_app
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="sesiones_conteo_contabilidad"
    )

    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierta')
    observaciones = models.TextField(blank=True, null=True)

    fecha_aplicacion = models.DateTimeField(blank=True, null=True)

    # Evitar colisión con inventario_app
    usuario_cierre = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cierres_conteo_contabilidad"
    )

    fecha_cierre = models.DateTimeField(blank=True, null=True)

    # Evitar colisión con inventario_app
    usuario_reapertura = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reaperturas_conteo_contabilidad"
    )

    fecha_reapertura = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Sesión de conteo"
        verbose_name_plural = "Sesiones de conteo"

    def __str__(self):
        return f"{self.nombre} — {self.get_estado_display()}"

    # -----------------------------------------------------
    # ASIENTOS INTERNOS (inventario_app)
    # -----------------------------------------------------
    def generar_asientos_conteo(self, usuario=None):
        items = self.lineas.all()

        total_incremento = sum(i.diferencia * i.precio_coste for i in items if i.diferencia > 0)
        total_disminucion = sum(abs(i.diferencia * i.precio_coste) for i in items if i.diferencia < 0)

        if total_incremento > 0:
            AsientoContable.objects.create(
                sesion_conteo=self,
                tipo="incremento",
                descripcion=f"Incremento inventario — Sesión {self.id}",
                debe_cuenta="300 Existencias",
                haber_cuenta="610 Variación existencias (incremento)",
                importe=total_incremento,
                usuario=usuario,
            )

        if total_disminucion > 0:
            AsientoContable.objects.create(
                sesion_conteo=self,
                tipo="disminucion",
                descripcion=f"Disminución inventario — Sesión {self.id}",
                debe_cuenta="610 Variación existencias (disminución)",
                haber_cuenta="300 Existencias",
                importe=total_disminucion,
                usuario=usuario,
            )

    # -----------------------------------------------------
    # ASIENTO CONTABLE REAL (contabilidad_app)
    # -----------------------------------------------------
    def generar_asiento_contable_real(self, usuario=None):
        from contabilidad_app.models import Asiento, AsientoLinea, Diario, CuentaContable

        items = self.lineas.all()

        total_incremento = sum(i.diferencia * i.precio_coste for i in items if i.diferencia > 0)
        total_disminucion = sum(abs(i.diferencia * i.precio_coste) for i in items if i.diferencia < 0)

        if total_incremento == 0 and total_disminucion == 0:
            return None

        diario = Diario.objects.get(codigo="INV")

        asiento = Asiento.objects.create(
            diario=diario,
            fecha=timezone.now().date(),
            descripcion=f"Ajuste inventario — Sesión {self.id}",
            referencia=f"Conteo {self.id}",
            usuario=usuario,
        )

        cuenta_existencias = CuentaContable.objects.get(codigo="300")
        cuenta_variacion = CuentaContable.objects.get(codigo="610")

        if total_incremento > 0:
            AsientoLinea.objects.create(
                asiento=asiento,
                cuenta=cuenta_existencias,
                descripcion=f"Incremento inventario sesión {self.id}",
                debe=total_incremento,
                haber=0,
            )
            AsientoLinea.objects.create(
                asiento=asiento,
                cuenta=cuenta_variacion,
                descripcion=f"Incremento inventario sesión {self.id}",
                debe=0,
                haber=total_incremento,
            )

        if total_disminucion > 0:
            AsientoLinea.objects.create(
                asiento=asiento,
                cuenta=cuenta_variacion,
                descripcion=f"Disminución inventario sesión {self.id}",
                debe=total_disminucion,
                haber=0,
            )
            AsientoLinea.objects.create(
                asiento=asiento,
                cuenta=cuenta_existencias,
                descripcion=f"Disminución inventario sesión {self.id}",
                debe=0,
                haber=total_disminucion,
            )

        return asiento


# =========================================================
# LÍNEAS DE CONTEO
# =========================================================

class ConteoLinea(models.Model):
    sesion = models.ForeignKey(ConteoSesion, related_name="lineas", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    precio_coste = models.DecimalField(max_digits=10, decimal_places=2)

    stock_teorico = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_contado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    motivo = models.CharField(max_length=200, blank=True, null=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)

    # Evitar colisión con inventario_app
    usuario_modifica = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="modificaciones_conteo_contabilidad"
    )

    fecha_modifica = models.DateTimeField(blank=True, null=True)

    @property
    def diferencia(self):
        return self.stock_contado - self.stock_teorico

    @property
    def importe_teorico(self):
        return self.stock_teorico * self.precio_coste if self.precio_coste else 0

    @property
    def importe_contado(self):
        return self.stock_contado * self.precio_coste if self.precio_coste else 0

    @property
    def importe_aumenta(self):
        if self.diferencia > 0:
            return self.diferencia * self.precio_coste
        return 0

    @property
    def importe_disminuye(self):
        if self.diferencia < 0:
            return abs(self.diferencia) * self.precio_coste
        return 0

    def save(self, *args, **kwargs):
        self.fecha_modifica = timezone.now()
        super().save(*args, **kwargs)


# =========================================================
# ASIENTOS INTERNOS (inventario_app)
# =========================================================

class AsientoContable(models.Model):
    TIPO_ASIENTO = [
        ("incremento", "Incremento de inventario"),
        ("disminucion", "Disminución de inventario"),
    ]

    sesion_conteo = models.ForeignKey(ConteoSesion, on_delete=models.CASCADE, related_name="asientos")
    tipo = models.CharField(max_length=20, choices=TIPO_ASIENTO)
    descripcion = models.CharField(max_length=255)

    debe_cuenta = models.CharField(max_length=50)
    haber_cuenta = models.CharField(max_length=50)

    importe = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    # Evitar colisión con inventario_app
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asientos_inventario_contabilidad"
    )

    def __str__(self):
        return f"Asiento {self.id} — {self.get_tipo_display()}"

    def revertir(self, usuario=None):
        return AsientoContable.objects.create(
            sesion_conteo=self.sesion_conteo,
            tipo=self.tipo,
            descripcion=f"Reversión del asiento {self.id}",
            debe_cuenta=self.haber_cuenta,
            haber_cuenta=self.debe_cuenta,
            importe=self.importe,
            usuario=usuario,
        )


# =========================================================
# MODELOS CONTABLES REALES (contabilidad_app)
# =========================================================

class Diario(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Diario"
        verbose_name_plural = "Diarios"

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"


class CuentaContable(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Cuenta contable"
        verbose_name_plural = "Cuentas contables"

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"


class Asiento(models.Model):
    diario = models.ForeignKey(Diario, on_delete=models.PROTECT)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    referencia = models.CharField(max_length=255, blank=True, null=True)
    # Aquí NO ponemos related_name para no chocar con nada
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"

    def __str__(self):
        return f"Asiento {self.id} — {self.descripcion}"


class AsientoLinea(models.Model):
    asiento = models.ForeignKey(Asiento, related_name="lineas", on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=255)
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Línea de asiento"
        verbose_name_plural = "Líneas de asiento"

    def __str__(self):
        return f"{self.cuenta.codigo} — D:{self.debe} / H:{self.haber}"
