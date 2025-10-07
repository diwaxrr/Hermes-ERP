# Archivo: reportes/urls.py

from django.urls import path
from .views import DashboardView, ReporteVentasView, ReporteInventarioView, ReporteFinancieroView


urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('ventas/', ReporteVentasView.as_view(), name='reporte-ventas'),
    path('financiero/', ReporteFinancieroView.as_view(), name='reporte-financiero'),
    path('inventario/', ReporteInventarioView.as_view(), name='reporte-inventario'),
]