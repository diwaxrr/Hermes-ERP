# Archivo: nomina/admin.py

from django.contrib import admin
from .models import Empleado, ConceptoNomina, PeriodoNomina, NominaEncabezado, NominaDetalle

class NominaDetalleInline(admin.TabularInline):
    model = NominaDetalle
    extra = 1
    raw_id_fields = ('concepto',)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombres', 'apellidos', 'puesto', 'departamento', 'activo')
    list_filter = ('departamento', 'tipo_contrato', 'activo')
    search_fields = ('cedula', 'nombres', 'apellidos', 'puesto')
    list_editable = ('activo',)

@admin.register(ConceptoNomina)
class ConceptoNominaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'naturaleza', 'cuenta_contable')
    list_filter = ('tipo', 'naturaleza')
    search_fields = ('codigo', 'nombre')

@admin.register(PeriodoNomina)
class PeriodoNominaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'fecha_inicio', 'fecha_fin', 'fecha_pago', 'estado')
    list_filter = ('estado',)
    search_fields = ('descripcion',)

@admin.register(NominaEncabezado)
class NominaEncabezadoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'periodo', 'total_devengos', 'total_deducciones', 'neto_a_pagar')
    list_filter = ('periodo',)
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'periodo__descripcion')
    readonly_fields = ('total_devengos', 'total_deducciones', 'neto_a_pagar')
    inlines = [NominaDetalleInline]