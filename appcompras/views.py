from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from inventario_app.models import Proveedor, Producto
from .services.importador_excel import ImportadorExcel

# Modelos del módulo de compras
from appcompras.models.albaran import AlbaranCompra
from appcompras.models.factura import FacturaCompra

# Servicio de recepción
from inventario_app.servicios.servicio_procesar_recepcion import ServicioProcesarRecepcion

# Contabilidad
from contabilidad_app.models import AsientoContable, CuentaContable


# ---------------------------------------------------------
# 1) IMPORTACIÓN EXCEL (TU CÓDIGO ORIGINAL)
# ---------------------------------------------------------

def importar_excel(request):
    proveedores = Proveedor.objects.all()

    if request.method == "POST" and request.POST.get("confirmar") == "1":
        archivo = request.FILES.get("archivo")
        proveedor_id = request.POST.get("proveedor")
        usuario = request.user

        servicio = ImportadorExcel(
            archivo=archivo,
            proveedor_id=proveedor_id,
            usuario=usuario,
            confirmar=True
        )

        resultado = servicio.ejecutar()

        return render(request, "appcompras/importar_excel.html", {
            **resultado,
            "proveedores": proveedores,
            "confirmado": True
        })

    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        proveedor_id = request.POST.get("proveedor")
        usuario = request.user

        servicio = ImportadorExcel(
            archivo=archivo,
            proveedor_id=proveveedor_id,
            usuario=usuario,
            confirmar=False
        )

        resultado = servicio.ejecutar()

        return render(request, "appcompras/importar_excel.html", {
            **resultado,
            "proveedores": proveedores,
            "archivo": archivo,
            "proveedor_id": proveedor_id
        })

    return render(request, "appcompras/importar_excel.html", {
        "proveedores": proveedores
    })


# ---------------------------------------------------------
# 2) CONFIRMACIÓN DE RECEPCIÓN DE ALBARÁN
# ---------------------------------------------------------

def confirmar_recepcion(request, albaran_id):

    albaran = get_object_or_404(AlbaranCompra, id=albaran_id)

    if request.method == "POST":

        resultados = []

        for linea in albaran.lineas.all():
            resultado = ServicioProcesarRecepcion.procesar_linea_albaran(linea)
            resultados.append(resultado)

        albaran.estado = AlbaranCompra.ESTADO_RECIBIDO
        albaran.save(update_fields=["estado"])

        messages.success(request, "Recepción procesada correctamente.")
        return redirect("detalle_albaran", albaran_id=albaran.id)

    return redirect("detalle_albaran", albaran_id=albaran.id)


# ---------------------------------------------------------
# 3) ENDPOINT UNIVERSAL PARA AUTOCOMPLETAR PRODUCTO
# ---------------------------------------------------------

@staff_member_required
def api_producto_detalle(request, pk):

    try:
        producto = Producto.objects.select_related("iva").get(pk=pk)
    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)

    return JsonResponse({
        "id": producto.id,
        "nombre_interno": producto.nombre_interno,
        "precio_compra": str(producto.precio_compra or 0),
        "iva": str(producto.iva.porcentaje if producto.iva else 0),
        "unidad_medida": getattr(producto, "unidad_medida", ""),
    })


# ---------------------------------------------------------
# 4) VISTA DEL ERP PARA MOSTRAR EL ALBARÁN
# ---------------------------------------------------------

@login_required
def ver_albaran(request, albaran_id):
    albaran = get_object_or_404(AlbaranCompra, id=albaran_id)
    return render(request, "appcompras/ver_albaran.html", {"albaran": albaran})


# ---------------------------------------------------------
# 5) GENERAR FACTURA DESDE ALBARÁN (BOTÓN AZUL)
# ---------------------------------------------------------

@login_required
def generar_factura_desde_albaran(request, albaran_id):

    albaran = get_object_or_404(AlbaranCompra, id=albaran_id)

    # Seguridad: solo si viene de pedido, está confirmado y no tiene factura
    if not albaran.pedido or albaran.estado != AlbaranCompra.ESTADO_CONFIRMADO or albaran.factura:
        messages.error(request, "No se puede generar factura desde este albarán.")
        return redirect("ver_albaran", albaran_id=albaran.id)

    # Crear factura
    factura = FacturaCompra.objects.create(
        proveedor=albaran.proveedor,
        fecha_factura=albaran.fecha_recepcion,
        observaciones=f"Generada automáticamente desde el Albarán {albaran.numero_albaran}",
    )

    # Copiar líneas
    for linea in albaran.lineas.all():
        factura.lineas.create(
            producto=linea.producto,
            cantidad=linea.cantidad,
            precio=linea.precio,
            iva=linea.iva,
        )

    # Enlazar factura ↔ albarán
    albaran.factura = factura
    albaran.estado = AlbaranCompra.ESTADO_FACTURADO
    albaran.save()

    # Crear asiento contable
    cuenta_compras = CuentaContable.objects.get(codigo="600")
    cuenta_iva = CuentaContable.objects.get(codigo="472")
    cuenta_proveedor = CuentaContable.objects.get(codigo="400")

    asiento = AsientoContable.objects.create(
        descripcion=f"Factura {factura.id} - {factura.proveedor.nombre}",
        fecha=factura.fecha_factura,
    )

    asiento.movimientos.create(
        cuenta=cuenta_compras,
        debe=factura.base_imponible_total(),
        haber=0
    )

    asiento.movimientos.create(
        cuenta=cuenta_iva,
        debe=factura.iva_total(),
        haber=0
    )

    asiento.movimientos.create(
        cuenta=cuenta_proveedor,
        debe=0,
        haber=factura.total_factura()
    )

    factura.asiento = asiento
    factura.save()

    messages.success(request, "Factura generada correctamente.")
    return redirect("ver_factura", factura_id=factura.id)


# ---------------------------------------------------------
# 6) NUEVO: VISTA PARA VER LA FACTURA GENERADA
# ---------------------------------------------------------

@login_required
def ver_factura(request, factura_id):
    factura = get_object_or_404(FacturaCompra, id=factura_id)
    return render(request, "appcompras/ver_factura.html", {"factura": factura})
