# Archivo: facturacion/admin.py

from django.contrib import admin
from .models import FacturaEncabezado, FacturaDetalle, Pago

class FacturaDetalleInline(admin.TabularInline):
    model = FacturaDetalle
    extra = 1
    raw_id_fields = ('producto',)

@admin.register(FacturaEncabezado)
class FacturaEncabezadoAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'fecha_emision', 'cliente', 'total', 'estado')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('numero_factura', 'cliente__nombre_comercial')
    readonly_fields = ('subtotal', 'impuesto', 'total')
    inlines = [FacturaDetalleInline]

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('factura', 'fecha_pago', 'monto', 'metodo_pago')
    list_filter = ('metodo_pago', 'fecha_pago')
    search_fields = ('factura__numero_factura', 'referencia')