from django.contrib import admin
from .models import Produccion, ProduccionLinea

class ProduccionLineaInline(admin.TabularInline):
    model = ProduccionLinea
    extra = 1

@admin.register(Produccion)
class ProduccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'escandallo', 'responsable', 'fecha')
    inlines = [ProduccionLineaInline]