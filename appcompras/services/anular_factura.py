from django.db import transaction
from django.utils import timezone
from contabilidad.models import AsientoContable, ApunteContable

@transaction.atomic
def servicio_anular_factura(factura, usuario):
    if factura.estado_factura == "anulada":
        return

    asiento_original = factura.asiento

    asiento_inv = AsientoContable.objects.create(
        fecha=timezone.now().date(),
        descripcion=f"Anulación factura compra {factura.id}",
        usuario=usuario,
    )

    for apunte in asiento_original.apuntes.all():
        ApunteContable.objects.create(
            asiento=asiento_inv,
            cuenta=apunte.cuenta,
            debe=apunte.haber,
            haber=apunte.debe,
        )

    for alb in factura.albaranes.all():
        alb.estado = "recibido"
        alb.save()

    factura.estado_factura = "anulada"
    factura.asiento_anulacion = asiento_inv
    factura.save()
