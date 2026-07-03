from django.contrib import admin
from .models.factura import FacturaCompra, FacturaCompraLinea
from .models.albaran import AlbaranCompraLinea
from inventario_app.models import Proveedor


class FacturaCompraLineaDevInline(admin.TabularInline):
    model = FacturaCompraLinea
    extra = 0
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


class AlbaranLineaDevInline(admin.TabularInline):
    model = AlbaranCompraLinea
    extra = 0
    can_delete = False
    fk_name = None  # no buscamos FK a FacturaCompra

    readonly_fields = [
        "albaran",
        "producto",
        "cantidad_recibida",
        "precio_unitario",
        "descuento_linea",
        "subtotal",
        "iva",
        "importe_impuestos",
        "total_linea",
    ]
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        factura_id = request.resolver_match.kwargs.get("object_id")

        if not factura_id:
            return qs.none()

        factura = FacturaCompra.objects.get(id=factura_id)

        return qs.filter(
            albaran__proveedor=factura.proveedor,
            albaran__estado="CONFIRMADO",
            albaran__factura_asociada__isnull=True,
        )


@admin.register(FacturaCompra, name="FacturaCompraDev")
class FacturaCompraDevAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_factura', 'estado_factura', 'total')
    list_filter = ('estado_factura', 'proveedor', 'fecha_factura')
    search_fields = ('id', 'proveedor__nombre')

    inlines = [
        AlbaranLineaDevInline,
        FacturaCompraLineaDevInline,
    ]

    exclude = ('albaranes',)

    readonly_fields = (
        'importe_subtotal',
        'importe_impuestos',
        'total',
    )

    class Media:
        js = ("appcompras/autocompletar_producto.js",)

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
