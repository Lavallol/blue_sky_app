from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("inventario/", include("inventario_app.urls")),
    path('escandallo/', include('escandallo_app.urls')),
]

