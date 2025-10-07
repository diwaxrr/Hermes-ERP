# Archivo: inventario/admin.py

from django.contrib import admin
from .models import Almacen, Stock, MovimientoInventario

# 1. Almacén (Simple)
@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activo')
    search_fields = ('nombre', 'codigo')
    list_filter = ('activo',)

# 2. Stock (Solo lectura, se actualiza por Signals)
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'almacen', 'cantidad')
    search_fields = ('producto__nombre', 'almacen__nombre')
    list_filter = ('almacen',)
    readonly_fields = ('producto', 'almacen', 'cantidad') # Para evitar edición manual

# 3. Movimiento de Inventario
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'almacen', 'tipo_movimiento', 'cantidad', 'referencia_doc')
    search_fields = ('producto__nombre', 'referencia_doc')
    list_filter = ('tipo_movimiento', 'almacen', 'fecha')
    
    # CAMBIO CLAVE: Usamos autocomplete_fields para buscar por nombre
    autocomplete_fields = ('producto', 'almacen')
    
    # Mantenemos raw_id_fields solo para el enlace contable
    raw_id_fields = ('asiento_contable_nucleo',)