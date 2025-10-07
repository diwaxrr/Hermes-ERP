from django.contrib import admin
from .models import ReporteConfiguracion

@admin.register(ReporteConfiguracion)
class ReporteConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_reporte', 'codigo', 'activo']
    list_filter = ['tipo_reporte', 'activo']
    search_fields = ['nombre', 'codigo']