from django.contrib import admin
from .models import (
    Moneda, CuentaContable, EntidadComercial, Producto,
    TransaccionEncabezado, MovimientoContable
)

# -------------------------------------------------------------
# 1. MODELOS BÁSICOS
# -------------------------------------------------------------

@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('nombre',)

@admin.register(EntidadComercial)
class EntidadComercialAdmin(admin.ModelAdmin):
    list_display = ('id',)
    list_filter = ('id',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('nombre',)
    search_fields = ('sku', 'nombre') 

# -------------------------------------------------------------
# 2. CUENTAS CONTABLES
# -------------------------------------------------------------

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'cuenta_padre')
    list_filter = ('naturaleza',)

# -------------------------------------------------------------
# 3. TRANSACCIONES CONTABLES
# -------------------------------------------------------------

# El MovimientoContable va inline (dentro del Encabezado)
class MovimientoContableInline(admin.TabularInline):
    model = MovimientoContable
    extra = 1 # Para mostrar 1 formulario vacío para añadir un movimiento
    raw_id_fields = ('cuenta',) # Usamos ID para buscar cuentas

@admin.register(TransaccionEncabezado)
class TransaccionEncabezadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'referencia')
    list_filter = ('fecha',)

    inlines = [MovimientoContableInline] # Mostramos los movimientos debajo