from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from .views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("inventario/", include("inventario_app.urls")),
    path("escandallos/", include("escandallo_app.urls")),
    path("produccion/", include("produccion.urls")),
    path("conteo/", include("inventario_app.urls_conteo_nuevo")),
    path('appcompras/', include('appcompras.urls')),
]