from django.urls import path
from . import views

urlpatterns = [
    # Escandallos
    path('', views.escandallo_list, name='escandallo_list'),
    path('<int:pk>/', views.escandallo_detalle, name='escandallo_detalle'),
    path('crear/', views.escandallo_crear, name='escandallo_crear'),
    path('<int:pk>/editar/', views.escandallo_editar, name='escandallo_editar'),
    path('<int:pk>/eliminar/', views.escandallo_eliminar, name='escandallo_eliminar'),

    # ⭐ INGREDIENTES ⭐
    path('<int:escandallo_id>/ingredientes/nuevo/',
         views.escandallo_ingrediente_crear,
         name='escandallo_ingrediente_crear'),

    path('ingrediente/<int:linea_id>/editar/',
         views.escandallo_ingrediente_editar,
         name='escandallo_ingrediente_editar'),

    path('ingrediente/<int:linea_id>/eliminar/',
         views.escandallo_ingrediente_eliminar,
         name='escandallo_ingrediente_eliminar'),

    # ⭐ NUEVO: AUTOCOMPLETAR PRECIO DEL PRODUCTO ⭐
    # Esta es la ruta que usará el JS para obtener el precio_compra
    path('precio-producto/<int:producto_id>/',
         views.obtener_precio_producto,
         name='precio_producto'),
]
