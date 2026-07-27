from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django import forms
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from datetime import date

# -----------------------------
# IMPORTAR MODELOS
# -----------------------------
from .models.pedido import PedidoCompra, PedidoCompraLinea
from .models.albaran import AlbaranCompra, AlbaranCompraLinea
from .models.factura import FacturaCompra, FacturaCompraLinea
from .models.condicion_pago import CondicionPago

from inventario_app.servicios.servicio_procesar_recepcion import ServicioProcesarRecepcion
from inventario_app.models import Producto
from inventario_app.models import Proveedor


#   FUNCIÓN GENERAL PARA RENDERIZAR PDF
# ============================================================

def render_pdf(template, context):
    html = render_to_string(template, context)
    return HttpResponse(html)


# ============================================================
#   MIXIN UNIVERSAL PARA AUTOCOMPLETADO
# ============================================================

class LineaAutocompletableMixin:
    class Media:
        js = ("appcompras/autocompletar_producto.js",)


# ============================================================
#   FORMULARIOS PROFESIONALES
# ============================================================

class PedidoCompraLineaForm(forms.ModelForm):
    class Meta:
        model = PedidoCompraLinea
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

class PedidoCompraLineaInline(LineaAutocompletableMixin, admin.TabularInline):
    model = PedidoCompraLinea
    form = PedidoCompraLineaForm
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


# ============================================================
#   ADMIN DEL PEDIDO
# ============================================================

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

    class Media:
        js = ("appcompras/autocompletar_producto.js",)

    def generar_albaran(self, request, pedido_id):
        pedido = get_object_or_404(PedidoCompra, id=pedido_id)

        if pedido.estado != "CONFIRMADO":
            messages.error(request, "El pedido debe estar CONFIRMADO para generar un albarán.")
            return redirect(reverse("admin:appcompras_pedidocompra_change", args=[pedido_id]))

        albaran = AlbaranCompra.objects.create(
            proveedor=pedido.proveedor,
            pedido=pedido,
            fecha_recepcion=pedido.fecha_prevista or pedido.fecha_pedido,
            estado="BORRADOR",
            observaciones=f"Generado automáticamente desde el Pedido {pedido.id}"
        )

        for linea in pedido.lineas.all():
            AlbaranCompraLinea.objects.create(
                albaran=albaran,
                producto=linea.producto,
                cantidad_recibida=linea.cantidad_pedida,
                precio_unitario=linea.precio_unitario,
                descuento_linea=linea.descuento_linea,
                iva=linea.iva,
            )

        albaran.recalcular_totales()

        pedido.estado = "CERRADO"
        pedido.save(update_fields=["estado"])

        messages.success(request, f"Albarán {albaran.id} generado correctamente.")
        return redirect(reverse("admin:appcompras_albarancompra_change", args=[albaran.id]))

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<int:pedido_id>/generar-albaran/',
                self.admin_site.admin_view(self.generar_albaran),
                name='appcompras_pedidocompra_generar_albaran'
            ),
            path('imprimir/<int:pk>/', self.admin_site.admin_view(self.imprimir_pedido),
                 name='appcompras_pedidocompra_imprimir'),
        ]
        return custom + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        pedido = PedidoCompra.objects.get(id=object_id)

        if extra_context is None:
            extra_context = {}

        extra_context["mostrar_boton_generar_albaran"] = (pedido.estado == "CONFIRMADO")

        return super().change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        if "_save" in request.POST and "_continue" not in request.POST:
            if obj.estado != "BORRADOR":
                request.POST = request.POST.copy()
                request.POST["_continue"] = "1"

        return super().response_change(request, obj)

    def imprimir_pedido(self, request, pk):
        pedido = get_object_or_404(PedidoCompra, pk=pk)
        return render_pdf("appcompras/pdf/pedido_compra.html", {"pedido": pedido})

    def crear_albaran_desde_pedidos(self, request, queryset):
        creados = 0

        for pedido in queryset:
            albaran = AlbaranCompra.objects.create(
                proveedor=pedido.proveedor,
                pedido=pedido,
                fecha_recepcion=pedido.fecha_pedido,
                estado='BORRADOR',
            )

            for linea in pedido.lineas.all():
                if linea.cantidad_pendiente <= 0:
                    continue

                AlbaranCompraLinea.objects.create(
                    albaran=albaran,
                    producto=linea.producto,
                    cantidad_recibida=linea.cantidad_pendiente,
                    precio_unitario=linea.precio_unitario,
                    descuento_linea=linea.descuento_linea,
                    iva=linea.iva,
                )

            albaran.recalcular_totales()
            creados += 1

        messages.success(request, f"Se han creado {creados} albaranes de compra.")

    crear_albaran_desde_pedidos.short_description = "Crear albarán desde pedidos seleccionados"

    actions = ["imprimir_seleccionados", "crear_albaran_desde_pedidos"]

    def imprimir_seleccionados(self, request, queryset):
        pedido = queryset.first()
        return render_pdf("appcompras/pdf/pedido_compra.html", {"pedido": pedido})

    imprimir_seleccionados.short_description = "Imprimir pedidos seleccionados"

# ---------------------------------------------------------
# BLOQUE NUEVO — LÍNEAS COPIADAS DESDE PEDIDO (SOLO VISUAL)
# ---------------------------------------------------------

def render_lineas_pedido_visual(self, obj):
    """
    Renderiza un bloque visual con las líneas del Pedido seleccionado.
    Este bloque NO es un inline y NO guarda datos.
    Solo muestra las líneas copiadas desde el Pedido.
    """
    if not obj.pedido:
        return mark_safe("<p style='color: #888;'>No hay pedido seleccionado.</p>")

    lineas = obj.pedido.lineas.all()

    html = """
    <h3 style='margin-top:20px;'>Líneas del Pedido (solo visual)</h3>
    <table style='width:100%; border-collapse: collapse;'>
        <thead>

            <tr style='background:#f0f0f0;'>
                <th>Fecha Pedido</th>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Precio</th>
                <th>Descuento</th>
                <th>Subtotal</th>
                <th>IVA</th>
                <th>Importe IVA</th>
                <th>Total con IVA</th>
                <th>Stock antes</th>
                <th>Stock después</th>
            </tr>
        </thead>
        <tbody>
    """

    for linea in lineas:
        subtotal = linea.cantidad * linea.precio_unitario
        importe_iva = subtotal * (linea.iva / 100)
        total_con_iva = subtotal + importe_iva

        html += f"""
            <tr>
                <td>{obj.pedido.fecha_pedido}</td>
                <td>{linea.producto.nombre}</td>
                <td>{linea.cantidad}</td>
                <td>{linea.precio_unitario:.2f}</td>
                <td>{linea.descuento_linea:.2f}</td>
                <td>{subtotal:.2f}</td>
                <td>{linea.iva}%</td>
                <td>{importe_iva:.2f}</td>
                <td>{total_con_iva:.2f}</td>
                <td>–</td>
                <td>–</td>
            </tr>
        """

    html += "</tbody></table>"

    return mark_safe(html)

# ============================================================
#   INLINES DEL ALBARÁN
# ============================================================

class AlbaranCompraLineaInline(LineaAutocompletableMixin, admin.TabularInline):
    model = AlbaranCompraLinea
    form = AlbaranCompraLineaForm
    extra = 1

    fields = (
        'producto',
        'cantidad_recibida',
        'precio_unitario',
        'descuento_linea',
        'subtotal_linea',
        'iva',
        'importe_iva',         
        'total_linea_con_iva',
        'stock_antes',
        'stock_despues',
    )

    readonly_fields = (
    'subtotal_linea',
    'importe_iva', 
    'total_linea_con_iva',
    'stock_antes',
    'stock_despues',
    )

    def subtotal_linea(self, obj):
        return f"{obj.subtotal:.2f}"

    def importe_iva(self, obj):
        return f"{obj.importe_iva:.2f}"

    def total_linea_con_iva(self, obj):
        return f"{obj.total_linea_con_iva:.2f}"


# ============================================================
#   ADMIN DEL ALBARÁN
# ============================================================

@admin.register(AlbaranCompra)
class AlbaranCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_recepcion', 'estado', 'total')
    list_filter = ('estado', 'proveedor', 'fecha_recepcion')
    search_fields = ('id', 'proveedor__nombre')
    inlines = [AlbaranCompraLineaInline]

    # 🟩 NUEVO BLOQUE — Rectángulo + Acción
    fieldsets = (
        ("Datos del Albarán", {
            "fields": ("proveedor", "fecha_recepcion", "estado", "total")
        }),
        ("Mercancía recibida desde Pedido", {
            "fields": ("pedido",),
            "description": "Seleccione un Pedido pendiente para copiar sus líneas al Albarán."
        }),
    )

    actions = ["reabrir_albaranes", "accion_copiar_lineas_desde_pedido", "cancelar_albaranes", "eliminar_albaranes"]

    def cancelar_albaranes(self, request, queryset):
        for alb in queryset:
            if alb.estado != "CONFIRMADO":
                messages.error(request, f"El albarán {alb.id} no está confirmado, no se puede cancelar.")
                continue

            for linea in alb.lineas.all():
                ServicioStock.revertir_stock(
                    producto=linea.producto,
                    cantidad=linea.cantidad,
                    origen=f"Cancelación AlbaránCompra #{alb.id}"
                )

            alb.estado = "CANCELADO"
            alb.save()

        messages.success(request, "Albaranes cancelados y stock revertido correctamente.")

    def accion_copiar_lineas_desde_pedido(self, request, queryset):
        for albaran in queryset:
            pedido = albaran.pedido

            if not pedido:
                messages.error(request, "El Albarán no tiene Pedido asociado.")
                continue

            lineas_pedido = PedidoCompraLinea.objects.filter(pedido=pedido)

            for linea in lineas_pedido:
                AlbaranCompraLinea.objects.create(
                    albaran=albaran,
                    producto=linea.producto,
                    cantidad_pedida=linea.cantidad,
                    cantidad_recibida=linea.cantidad,
                    precio_unitario=linea.precio_unitario,
                    descuento=linea.descuento,
                    iva=linea.iva,
                    subtotal=linea.subtotal,
                    total_con_iva=linea.total_con_iva,
                    stock_antes=linea.producto.stock,
                    stock_despues=linea.producto.stock + linea.cantidad
                )

                linea.producto.stock += linea.cantidad
                linea.producto.save()

            pedido.estado = "CERRADO"
            pedido.save()

            messages.success(request, f"Líneas copiadas y Pedido {pedido.id} cerrado.")

    accion_copiar_lineas_desde_pedido.short_description = "Copiar líneas del Pedido y cerrar Pedido"

    readonly_fields = (
        'subtotal',
        'iva_total',
        'total',
        'render_lineas_pedido_visual',
    )

    def render_lineas_pedido_visual(self, obj):
        """
        Renderiza un bloque visual con las líneas del Pedido seleccionado.
        Este bloque NO es un inline y NO guarda datos.
        Solo muestra las líneas copiadas desde el Pedido.
        """
        if not obj.pedido:
            return mark_safe("<p style='color: #888;'>No hay pedido seleccionado.</p>

        lineas = obj.pedido.lineas.all()

        html = """
        <h3 style='margin-top:20px;'>Líneas del Pedido (solo visual)</h3>
        <table style='width:100%; border-collapse: collapse;'>
            <thead>
                <tr style='background:#f0f0f0;'>
                    <th>Fecha Pedido</th>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio</th>
                    <th>Descuento</th>
                    <th>Subtotal</th>
                    <th>IVA</th>
                    <th>Importe IVA</th>
                    <th>Total con IVA</th>
                    <th>Stock antes</th>
                    <th>Stock después</th>
                </tr>
            </thead>
            <tbody>
        """

        for linea in lineas:
            subtotal = linea.cantidad * linea.precio_unitario
            importe_iva = subtotal * (linea.iva / 100)
            total_con_iva = subtotal + importe_iva

            html += f"""
                <tr>
                    <td>{obj.pedido.fecha_pedido}</td>
                    <td>{linea.producto.nombre}</td>
                    <td>{linea.cantidad}</td>
                    <td>{linea.precio_unitario:.2f}</td>
                    <td>{linea.descuento_linea:.2f}</td>
                    <td>{subtotal:.2f}</td>
                    <td>{linea.iva}%</td>
                    <td>{importe_iva:.2f}</td>
                    <td>{total_con_iva:.2f}</td>
                    <td>–</td>
                    <td>–</td>
                </tr>
            """

        html += "</tbody></table>"

        return mark_safe(html)

    class Media:
        js = ("appcompras/autocompletar_producto.js",)

    def api_producto(self, request, producto_id):
        producto = Producto.objects.get(id=producto_id)
        return JsonResponse({
            "precio": float(producto.precio_compra),
            "iva": producto.iva.porcentaje if producto.iva else 0,
        })

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

    def procesar_recepcion(self, request, albaran_id):
        albaran = AlbaranCompra.objects.get(id=albaran_id)
        servicio = ServicioProcesarRecepcion()

        for linea in albaran.lineas.all():
            servicio.procesar_linea_albaran(linea)

            # --- Integración del Servicio Central de Stock ---
            ServicioStock.incrementar_stock(
                producto=linea.producto,
                cantidad=linea.cantidad,
                origen=f"AlbaránCompra #{albaran.id}"
            )

        albaran.estado = "CONFIRMADO"
        albaran.save()

        messages.success(request, "Recepción procesada correctamente.")
        return redirect(reverse("admin:appcompras_albarancompra_change", args=[albaran_id]))

    def imprimir_albaran(self, request, pk):
        albaran = get_object_or_404(AlbaranCompra, pk=pk)
        return render_pdf("appcompras/pdf/albaran_compra.html", {"albaran": albaran})

    def reabrir_albaranes(self, request, queryset):
        if not request.user.has_perm("appcompras.puede_reabrir_albaranes_compra"):
           messages.error(request, "No tiene permiso para reabrir albaranes.")
           return

        for alb in queryset:
            # Si ya está en borrador, no se puede reabrir
            if alb.estado == "BORRADOR":
               messages.error(request, f"El albarán {alb.id} ya está en borrador.")
               continue

            # Reabrir CONFIRMADO o CANCELADO → volver a BORRADOR
            alb.estado = "BORRADOR"
            alb.save()

        messages.success(request, "Albaranes reabiertos correctamente.")

    reabrir_albaranes.short_description = "Reabrir albaranes seleccionados"

    def eliminar_albaranes(self, request, queryset):
        for alb in queryset:
            if alb.estado in ["CONFIRMADO", "FACTURADO"]:
                messages.error(
                    request,
                    f"No se puede eliminar el albarán {alb.id} porque está {alb.estado.lower()}."
                )
                continue

            alb.delete()

        messages.success(request, "Albaranes eliminados correctamente.")

    actions = ["reabrir_albaranes", "cancelar_albaranes", "eliminar_albaranes"]

    def cancelar_albaranes(self, request, queryset):
        for alb in queryset:
            if alb.estado != "CONFIRMADO":
                messages.error(request, f"El albarán {alb.id} no está confirmado, no se puede cancelar.")
                continue

            alb.estado = "CANCELADO"
            alb.save()

        messages.success(request, "Albaranes cancelados correctamente.")

    # Copia automática de líneas del Pedido al crear el Albarán
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Si el usuario seleccionó un Pedido y el Albarán es nuevo
        if obj.pedido and not change:
            lineas_pedido = PedidoCompraLinea.objects.filter(pedido=obj.pedido)

            for linea in lineas_pedido:
                AlbaranCompraLinea.objects.create(
                    albaran=obj,
                    producto=linea.producto,
                    cantidad_pedida=linea.cantidad_pedida,
                    cantidad_recibida=linea.cantidad_pedida,
                    precio_unitario=linea.precio_unitario,
                    descuento=linea.descuento_linea,
                    iva=linea.iva,
                    subtotal=linea.subtotal,
                    total_linea=linea.total_linea,
                    stock_antes=linea.producto.stock_actual,
                    stock_despues=linea.producto.stock_actual + linea.cantidad_pedida
                )

                linea.producto.stock_actual += linea.cantidad_pedida
                linea.producto.save()

            obj.pedido.estado = "CERRADO"
            obj.pedido.save()

# ============================================================
#   INLINES DE LA FACTURA
# ============================================================

class FacturaCompraLineaInline(LineaAutocompletableMixin, admin.TabularInline):
    model = FacturaCompraLinea
    extra = 1
    readonly_fields = ('total',)
    fields = (
        'producto',
        'cantidad',
        'precio_unitario',
        'importe_descuento',
        'iva',
        'importe_impuestos',
        'total',
    )


# ============================================================
#   INLINE PARA ASOCIAR ALBARANES A FACTURA (ManyToMany)
# ============================================================

class AlbaranEnFacturaInline(admin.TabularInline):
    model = FacturaCompra.albaranes.through
    extra = 0
    verbose_name = "Albarán asociado"
    verbose_name_plural = "Albaranes asociados"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtrar solo albaranes del proveedor de la factura
        if db_field.name == "albarancompra":
            factura_id = request.resolver_match.kwargs.get("object_id")
            if factura_id:
                factura = FacturaCompra.objects.filter(id=factura_id).first()
                if factura:
                    kwargs["queryset"] = AlbaranCompra.objects.filter(
                        proveedor=factura.proveedor
                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ============================================================
#   ADMIN DE FACTURA
# ============================================================

@admin.register(FacturaCompra)
class FacturaCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_factura', 'estado_factura', 'total')
    list_filter = ('estado_factura', 'proveedor', 'fecha_factura')
    search_fields = ('id', 'proveedor__nombre')

    inlines = [AlbaranEnFacturaInline, FacturaCompraLineaInline]

    # Ocultamos el ManyToMany crudo, lo gestionamos solo por inline
    exclude = ('albaranes',)

    # Campo de totales + tabla profesional de albaranes
    readonly_fields = (
        'importe_subtotal',
        'importe_impuestos',
        'total',
        'tabla_albaranes',
    )

    class Media:
        js = ("appcompras/autocompletar_producto.js",)

    # Tabla HTML estilizada al estilo ERP profesional
    def tabla_albaranes(self, obj):
        if not obj.pk or not obj.albaranes.exists():
            return "—"

        filas = []
        for a in obj.albaranes.all():
            url = reverse("admin:appcompras_albarancompra_change", args=[a.id])
            filas.append(
                f"""
                <tr>
                    <td style="border:1px solid #ccc; padding:4px;">
                        <a href="{url}">Albarán {a.id}</a>
                    </td>
                    <td style="border:1px solid #ccc; padding:4px;">{a.fecha_recepcion}</td>
                    <td style="border:1px solid #ccc; padding:4px; text-align:right;">{a.total} €</td>
                    <td style="border:1px solid #ccc; padding:4px;">{a.estado}</td>
                </tr>
                """
            )

        tabla = f"""
        <table style="border-collapse:collapse; width:70%; margin-top:4px;">
            <thead>
                <tr style="background-color:#f0f0f0;">
                    <th style="border:1px solid #ccc; padding:4px;">Nº Albarán</th>
                    <th style="border:1px solid #ccc; padding:4px;">Fecha</th>
                    <th style="border:1px solid #ccc; padding:4px;">Importe</th>
                    <th style="border:1px solid #ccc; padding:4px;">Estado</th>
                </tr>
            </thead>
            <tbody>
                {''.join(filas)}
            </tbody>
        </table>
        """
        return mark_safe(tabla)

    tabla_albaranes.short_description = "Albaranes asociados"

    # AUTOCOMPLETAR CONDICIÓN DE PAGO ANTES DEL POST
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if "condicion_pago" in form.base_fields:
            form.base_fields["condicion_pago"].required = False

        if request.method == "POST":
            proveedor_id = request.POST.get("proveedor")
            if proveedor_id:
                try:
                    proveedor = Proveedor.objects.get(id=proveedor_id)
                    if proveedor.condicion_pago:
                        form.base_fields["condicion_pago"].initial = proveedor.condicion_pago.id
                except Proveedor.DoesNotExist:
                    pass

        return form

    # AUTOCOMPLETAR ANTES DEL PRIMER GUARDADO
    def save_model(self, request, obj, form, change):

        if not obj.condicion_pago_id and obj.proveedor and obj.proveedor.condicion_pago:
            obj.condicion_pago = obj.proveedor.condicion_pago

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
                    iva=linea.iva,
                    importe_impuestos=linea.importe_impuestos,
                    total=linea.total_linea,
                )

            alb.estado = "FACTURADO"
            alb.factura = obj
            alb.save()

        obj.recalcular_totales()

        messages.success(request, "Líneas copiadas y albaranes cerrados correctamente.")

    def imprimir_factura(self, request, pk):
        factura = get_object_or_404(FacturaCompra, pk=pk)
        return render_pdf("appcompras/pdf/factura_compra.html", {"factura": factura})
