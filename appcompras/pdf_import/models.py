from django.conf import settings
from django.db import models
from django.utils import timezone

from proveedores.models import Proveedor
from productos.models import Producto
from compras.models import Compra, CompraLinea


class DocumentoPDFImportado(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('error', 'Error'),
        ('parcial', 'Procesado parcialmente'),
    ]

    TIPO_DOCUMENTO_CHOICES = [
        ('albaran', 'Albarán'),
        ('factura', 'Factura'),
        ('presupuesto', 'Presupuesto'),
    ]

    archivo = models.FileField(upload_to='compras/pdf_import/')
    proveedor_detectado = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_pdf'
    )
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='factura'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    fecha_importacion = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_pdf_importados'
    )

    numero_documento = models.CharField(max_length=100, blank=True)
    fecha_documento = models.DateField(null=True, blank=True)
    total_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_documento = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    es_pdf_nativo = models.BooleanField(default=True)
    errores_detectados = models.TextField(blank=True)
    datos_brutos = models.JSONField(blank=True, null=True)

    compra_generada = models.OneToOneField(
        Compra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documento_pdf_origen'
    )

    class Meta:
        verbose_name = 'Documento PDF importado'
        verbose_name_plural = 'Documentos PDF importados'
        ordering = ['-fecha_importacion']

    def __str__(self):
        return f'{self.get_tipo_documento_display()} {self.numero_documento or "sin número"}'


class LineaPDFImportada(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('corregida', 'Corregida'),
        ('confirmada', 'Confirmada'),
        ('descartada', 'Descartada'),
    ]

    documento = models.ForeignKey(
        DocumentoPDFImportado,
        on_delete=models.CASCADE,
        related_name='lineas'
    )

    producto_detectado = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lineas_pdf_importadas'
    )
    referencia_proveedor = models.CharField(max_length=100, blank=True)
    descripcion = models.CharField(max_length=255, blank=True)

    cantidad = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_linea = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    observaciones = models.TextField(blank=True)

    compra_linea_generada = models.OneToOneField(
        CompraLinea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linea_pdf_origen'
    )

    indice_linea = models.PositiveIntegerField(default=0)
    datos_brutos = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Línea PDF importada'
        verbose_name_plural = 'Líneas PDF importadas'
        ordering = ['documento', 'indice_linea']

    def __str__(self):
        return f'Línea {self.indice_linea} de {self.documento_id}'


class PlantillaProveedor(models.Model):
    proveedor = models.OneToOneField(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='plantilla_pdf'
    )
    nombre = models.CharField(max_length=100)
    version = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    json_plantilla = models.JSONField()

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plantilla de proveedor para PDF'
        verbose_name_plural = 'Plantillas de proveedores para PDF'

    def __str__(self):
        return f'Plantilla PDF {self.proveedor.nombre} ({self.version or "v1"})'


class HistorialPDF(models.Model):
    ACCION_CHOICES = [
        ('subida', 'Subida de PDF'),
        ('deteccion_proveedor', 'Detección de proveedor'),
        ('extraccion_texto', 'Extracción de texto'),
        ('interpretacion', 'Interpretación'),
        ('previsualizacion', 'Previsualización'),
        ('conversion_compra', 'Conversión a compra'),
        ('error', 'Error'),
        ('otro', 'Otro'),
    ]

    documento = models.ForeignKey(
        DocumentoPDFImportado,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_pdf_import'
    )
    accion = models.CharField(
        max_length=50,
        choices=ACCION_CHOICES,
        default='otro'
    )
    detalle = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Historial de documento PDF'
        verbose_name_plural = 'Historial de documentos PDF'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_accion_display()} - {self.documento_id} - {self.fecha:%Y-%m-%d %H:%M}'
