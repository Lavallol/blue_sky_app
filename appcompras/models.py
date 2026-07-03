from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django import forms
from django.template.loader import render_to_string

# -----------------------------
# IMPORTAR MODELOS
# -----------------------------
from .models.pedido import PedidoCompra, PedidoCompraLinea
from .models.albaran import AlbaranCompra, AlbaranCompraLinea
from .models.factura import FacturaCompra, FacturaCompraLinea
from .models.condicion_pago import CondicionPago

# Importar servicios
from inventario_app.servicios.servicio_procesar_recepcion import ServicioProcesarRecepcion
from appcompras.services.anular_factura import servicio_anular_factura
from inventario_app.models import Producto


# ============================================================
#   FUNCIÓN GENERAL PARA RENDERIZAR PDF (HTML por ahora)
# ============================================================

def render_pdf(template, context):
    html = render_to_string(template, context)
    return HttpResponse(html)


# ============================================================
#   FORMULARIO PROFESIONAL PARA AUTOCOMPLETADO (ALBARÁN)
# ============================================================

class AlbaranCompraLineaForm(forms.ModelForm):
    class Meta:
        model = AlbaranCompraLinea
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        producto = cleaned.get("producto")
        precio_unitario = cleaned.get("precio_unitario")
        iva = cleaned.get("iva")

        if producto and (precio_unitario is None or precio_unitario == 0):
            cleaned["precio_unitario"] = producto.precio_compra

        if producto and not iva:
            cleaned["iva"] = producto.iva.porcentaje if producto.iva else 21

        return cleaned


# ============================================================
#   INLINES DEL PEDIDO
# ============================================================

class PedidoCompraLineaInline(admin.TabularInline):
    model = PedidoCompraLinea
    extra = 1
    readonly_fields = ('subtotal', 'iva_importe', 'total_linea')
    fields = (
        'producto',
        'cantidad_pedida',
        'cantidad_recibida',
        'precio_unitario',
        'descuento_linea',
        'iva',
        'subtotal',
        'iva_importe',
        'total_linea',
    )


@admin.register(PedidoCompra)
class PedidoCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_pedido', 'estado', 'subtotal', 'iva_total', 'total')
    list_filter = ('estado', 'proveedor', 'fecha_pedido')
    search_fields = ('id', 'proveedor__nombre')
    inlines = [PedidoCompraLineaInline]

    readonly_fields = (
        'subtotal_antes_descuento',
        'importe_descuento_global',
        'subtotal',
        'iva_total',
        'total',
        'created_at',
        'updated_at',
    )

    # ---------------------------
    # IMPRESIÓN INDIVIDUAL
    # ---------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('imprimir/<int:pk>/', self.admin_site.admin_view(self.imprimir_pedido),
                 name='appcompras_pedidocompra_imprimir'),
        ]
        return custom + urls

    def imprimir_pedido(self, request, pk):
        pedido = get_object_or_404(PedidoCompra, pk=pk)
        return render_pdf("appcompras/pdf/pedido_compra.html", {"pedido": pedido})

    # ---------------------------
    # ACCIÓN MASIVA
    # ---------------------------
    def imprimir_seleccionados(self, request, queryset):
        pedido = queryset.first()
        return render_pdf("appcompras/pdf/pedido_compra.html", {"pedido": pedido})

    imprimir_seleccionados.short_description = "Imprimir pedidos seleccionados"
    actions = ["imprimir_seleccionados"]


# ============================================================
#   INLINES DEL ALBARÁN
# ============================================================

class AlbaranCompraLineaInline(admin.TabularInline):
    model = AlbaranCompraLinea
    form = AlbaranCompraLineaForm
    extra = 1
    readonly_fields = ('total_linea', 'stock_antes', 'stock_despues')
    fields = (
        'producto',
        'cantidad_recibida',
        'precio_unitario',
        'descuento_linea',
        'iva',
        'total_linea',
        'stock_antes',
        'stock_despues',
    )


# ============================================================
#   ADMIN DEL ALBARÁN
# ============================================================

@admin.register(AlbaranCompra)
class AlbaranCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_recepcion', 'estado', 'total')
    list_filter = ('estado', 'proveedor', 'fecha_recepcion')
    search_fields = ('id', 'proveedor__nombre')
    inlines = [AlbaranCompraLineaInline]

    readonly_fields = ('subtotal', 'iva_total', 'total')

    class Media:
        js = ("admin/js/albaran_autocomplete.js",)

    # ---------------------------
    # API AUTOCOMPLETADO
    # ---------------------------
    def api_producto(self, request, producto_id):
        producto = Producto.objects.get(id=producto_id)
        return JsonResponse({
            "precio_compra": float(producto.precio_compra),
            "iva_id": producto.iva.id if producto.iva else None,
        })

    # ---------------------------
    # URLs personalizadas
    # ---------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('api/producto/<int:producto_id>/', self.admin_site.admin_view(self.api_producto),
                 name='api_producto'),
            path('<int:albaran_id>/procesar-recepcion/', self.admin_site.admin_view(self.procesar_recepcion),
                 name='appcompras_albarancompra_procesar_recepcion'),
            path('imprimir/<int:pk>/', self.admin_site.admin_view(self.imprimir_albaran),
                 name='appcompras_albarancompra_imprimir'),
        ]
        return custom + urls

    # ---------------------------
    # PROCESAR RECEPCIÓN
    # ---------------------------
    def procesar_recepcion(self, request, albaran_id):
        albaran = AlbaranCompra.objects.get(id=albaran_id)
        servicio = ServicioProcesarRecepcion()

        for linea in albaran.lineas.all():
            servicio.procesar_linea_albaran(linea)

        albaran.estado = "CONFIRMADO"
        albaran.save()

        messages.success(request, "Recepción procesada correctamente.")
        return redirect(reverse("admin:appcompras_albarancompra_change", args=[albaran_id]))

    # ---------------------------
    # IMPRESIÓN INDIVIDUAL
    # ---------------------------
    def imprimir_albaran(self, request, pk):
        albaran = get_object_or_404(AlbaranCompra, pk=pk)
        return render_pdf("appcompras/pdf/albaran_compra.html", {"albaran": albaran})

    # ---------------------------
    # ACCIÓN MASIVA: REABRIR ALBARANES
    # ---------------------------
    def reabrir_albaranes(self, request, queryset):
        if not request.user.has_perm("appcompras.puede_reabrir_albaranes_compra"):
            messages.error(request, "No tiene permiso para reabrir albaranes.")
            return

        for alb in queryset:
            alb.estado = "CONFIRMADO"
            alb.save()

        messages.success(request, "Albaranes reabiertos correctamente.")

    reabrir_albaranes.short_description = "Reabrir albaranes seleccionados"
    actions = ["reabrir_albaranes"]


# ============================================================
#   INLINES DE LA FACTURA
# ============================================================

class FacturaCompraLineaInline(admin.TabularInline):
    model = FacturaCompraLinea
    extra = 1
    readonly_fields = ('total',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'importe_descuento', 'importe_impuestos', 'total')


# ============================================================
#   ADMIN DE FACTURA
# ============================================================

@admin.register(FacturaCompra)
class FacturaCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_factura', 'estado_factura', 'total')
    list_filter = ('estado_factura', 'proveedor', 'fecha_factura')
    search_fields = ('id', 'proveedor__nombre')
    inlines = [FacturaCompraLineaInline]

    readonly_fields = ('importe_subtotal', 'importe_impuestos', 'total')

    change_form_template = "admin/appcompras/facturacompra/change_form.html"

    # ---------------------------
    # URLs personalizadas
    # ---------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('seleccionar-albaranes/<int:factura_id>/',
                 self.admin_site.admin_view(self.seleccionar_albaranes_view),
                 name='appcompras_facturacompra_seleccionar_albaranes'),
            path('imprimir/<int:pk>/', self.admin_site.admin_view(self.imprimir_factura),
                 name='appcompras_facturacompra_imprimir'),
            path('anular/<int:pk>/', self.admin_site.admin_view(self.anular_factura_view),
                 name='appcompras_facturacompra_anular'),
        ]
        return custom + urls

    # ---------------------------
    # SELECCIONAR ALBARANES
    # ---------------------------
    def seleccionar_albaranes_view(self, request, factura_id):
        factura = get_object_or_404(FacturaCompra, pk=factura_id)

        albaranes = AlbaranCompra.objects.filter(
            proveedor=factura.proveedor,
            estado="CONFIRMADO",
            factura__isnull=True
        )

        if request.method == "POST":
            ids = request.POST.getlist("albaran_ids")
            request.session["albaranes_factura"] = ids
            return redirect(reverse("admin:appcompras_facturacompra_change", args=[factura.id]))

        return render(
            request,
            "admin/appcompras/facturacompra/seleccionar_albaranes.html",
            {"factura": factura, "albaranes": albaranes},
        )

    # ---------------------------
    # GUARDAR: COPIAR LÍNEAS Y CERRAR ALBARANES
    # ---------------------------
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        ids = request.session.pop("albaranes_factura", None)
        if not ids:
            return

        albaranes = AlbaranCompra.objects.filter(id__in=ids)

        for alb in albaranes:
            for linea in alb.lineas.all():
                FacturaCompraLinea.objects.create(
                    factura=obj,
                    producto=linea.producto,
                    cantidad=linea.cantidad_recibida,
                    precio_unitario=linea.precio_unitario,
                    importe_descuento=linea.descuento_linea,
                    importe_impuestos=linea.iva,
                    total=linea.total_linea,
                )

            alb.estado = "FACTURADO"
            alb.factura = obj
            alb.save()

        messages.success(request, "Líneas copiadas y albaranes cerrados correctamente.")

    # ---------------------------
    # IMPRESIÓN INDIVIDUAL
    # ---------------------------
    def imprimir_factura(self, request, pk):
        factura = get_object_or_404(FacturaCompra, pk=pk)
        return render_pdf("appcompras/pdf/factura_compra.html", {"factura": factura})

    # ---------------------------
    # ANULAR FACTURA
    # ---------------------------
    def anular_factura_view(self, request, pk):
        factura = get_object_or_404(FacturaCompra, pk=pk)

        if not request.user.has_perm("appcompras.puede_anular_facturas_compra"):
            messages.error(request, "No tiene permiso para anular facturas.")
            return redirect(reverse("admin:appcompras_facturacompra_change", args=[pk]))

        servicio_anular_factura(factura, request.user)

        messages.success(request, "Factura anulada correctamente con reversión contable.")
        return redirect(reverse("admin:appcompras_facturacompra_change", args=[pk]))

    # ---------------------------
    # ACCIÓN MASIVA: ANULAR
    # ---------------------------
    def anular_seleccionadas(self, request, queryset):
        if not request.user.has_perm("appcompras.puede_anular_facturas_compra"):
            messages.error(request, "No tiene permiso para anular facturas.")
            return

        for factura in queryset:
            servicio_anular_factura(factura, request.user)

        messages.success(request, "Facturas anuladas correctamente.")

    anular_seleccionadas.short_description = "Anular facturas seleccionadas"
    actions = ["anular_seleccionadas"]
