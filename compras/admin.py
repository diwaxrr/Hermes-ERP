# Archivo: compras/admin.py

from django.contrib import admin
from .models import OrdenCompra, OrdenCompraDetalle, RecepcionCompra

class OrdenCompraDetalleInline(admin.TabularInline):
    model = OrdenCompraDetalle
    extra = 1
    raw_id_fields = ('producto',)

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'fecha_emision', 'proveedor', 'total', 'estado')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('numero_orden', 'proveedor__nombre_comercial')
    readonly_fields = ('subtotal', 'impuesto', 'total')
    inlines = [OrdenCompraDetalleInline]

@admin.register(RecepcionCompra)
class RecepcionCompraAdmin(admin.ModelAdmin):
    list_display = ('referencia', 'orden_compra', 'fecha_recepcion')
    list_filter = ('fecha_recepcion',)
    search_fields = ('referencia', 'orden_compra__numero_orden')