from django.urls import path
from . import views

urlpatterns = [
    path('', views.produccion_lista, name='produccion_lista'),
    path('crear/', views.produccion_crear, name='produccion_crear'),
    path('<int:pk>/', views.produccion_detalle, name='produccion_detalle'),
]