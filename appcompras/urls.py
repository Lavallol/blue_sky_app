from django.urls import path
from . import views
from . import views_api
from .views import api_producto_detalle

app_name = "appcompras"

urlpatterns = [
    # Importación Excel
    path('importar_excel/', views.importar_excel, name='importar_excel'),

    # ❌ ELIMINAR — API antigua que ya no existe
    # path('api/producto/<int:producto_id>/', views_api.api_producto_info, name='api_producto_info'),

    # Endpoint universal para autocompletado (Pedido, Albarán, Factura)
    path('api/producto/detalle/<int:pk>/', api_producto_detalle, name='api_producto_detalle'),

    # ⭐ Endpoint correcto para PedidoCompra
    path(
        'api/pedidocompra/producto/<int:producto_id>/',
        views_api.api_producto_pedido,
        name='api_producto_pedido'
    ),

    # Vista del ERP para mostrar el albarán
    path('albaran/<int:albaran_id>/', views.ver_albaran, name='ver_albaran'),

    # Generar factura desde albarán
    path('albaran/<int:albaran_id>/generar_factura/',
         views.generar_factura_desde_albaran,
         name='generar_factura_desde_albaran'),

    # Vista para ver la factura generada
    path('factura/<int:factura_id>/',
         views.ver_factura,
         name='ver_factura'),
]
