# Archivo: reportes/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from central.models import Producto, EntidadComercial, TransaccionEncabezado
from inventario.models import Stock, MovimientoInventario
from facturacion.models import FacturaEncabezado, Pago
from compras.models import OrdenCompra
from nomina.models import NominaEncabezado, Empleado
from rest_framework.permissions import IsAuthenticated

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Dashboard ejecutivo con métricas clave"""
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        inicio_anio = hoy.replace(month=1, day=1)
        
        # Ventas del mes
        ventas_mes = FacturaEncabezado.objects.filter(
            fecha_emision__gte=inicio_mes,
            estado='E'  # Emitidas
        ).aggregate(
            total_ventas=Sum('total'),
            cantidad_facturas=Count('id')
        )
        
        # Inventario valorizado
        inventario_valorizado = Stock.objects.aggregate(
            total_valor=Sum('cantidad')  # Aquí se podría multiplicar por costo
        )
        
        # Cuentas por cobrar
        cuentas_por_cobrar = FacturaEncabezado.objects.filter(
            estado='E'  # Emitidas (no pagadas)
        ).aggregate(total_por_cobrar=Sum('total'))
        
        # Gastos de nómina del mes
        gastos_nomina = NominaEncabezado.objects.filter(
            periodo__fecha_inicio__gte=inicio_mes
        ).aggregate(total_nomina=Sum('neto_a_pagar'))
        
        # Órdenes de compra pendientes
        compras_pendientes = OrdenCompra.objects.filter(
            estado__in=['E', 'R']  # Emitidas o Recibidas parcialmente
        ).aggregate(
            total_compras=Sum('total'),
            cantidad_ordenes=Count('id')
        )
        
        datos_dashboard = {
            'ventas': {
                'total_mes': ventas_mes['total_ventas'] or 0,
                'facturas_mes': ventas_mes['cantidad_facturas'] or 0,
            },
            'inventario': {
                'valor_total': inventario_valorizado['total_valor'] or 0,
                'productos_activos': Producto.objects.filter(activo=True).count(),
            },
            'finanzas': {
                'por_cobrar': cuentas_por_cobrar['total_por_cobrar'] or 0,
                'gastos_nomina': gastos_nomina['total_nomina'] or 0,
                'compras_pendientes': compras_pendientes['total_compras'] or 0,
            },
            'resumen': {
                'clientes_activos': EntidadComercial.objects.filter(activo=True, tipo__in=['C', 'A']).count(),
                'proveedores_activos': EntidadComercial.objects.filter(activo=True, tipo__in=['P', 'A']).count(),
                'empleados_activos': Empleado.objects.filter(activo=True).count(),
            }
        }
        
        return Response(datos_dashboard)

class ReporteVentasView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Reporte detallado de ventas"""
        # Parámetros de fecha (opcionales)
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        ventas = FacturaEncabezado.objects.filter(estado='E')
        
        if fecha_inicio:
            ventas = ventas.filter(fecha_emision__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha_emision__lte=fecha_fin)
        
        datos_ventas = ventas.aggregate(
            total_ventas=Sum('total'),
            promedio_venta=Avg('total'),
            cantidad_facturas=Count('id')
        )
        
        # Top 5 clientes
        top_clientes = ventas.values(
            'cliente__nombre_comercial'
        ).annotate(
            total_compras=Sum('total')
        ).order_by('-total_compras')[:5]
        
        return Response({
            'resumen': datos_ventas,
            'top_clientes': list(top_clientes)
        })

class ReporteInventarioView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Reporte de inventario y stock"""
        # Productos con stock bajo (menos de 10 unidades)
        stock_bajo = Stock.objects.filter(
            cantidad__lt=10
        ).select_related('producto', 'almacen')
        
        stock_bajo_data = [
            {
                'producto': item.producto.nombre,
                'almacen': item.almacen.nombre,
                'cantidad': float(item.cantidad),
                'sku': item.producto.codigo_sku
            }
            for item in stock_bajo
        ]
        
        # Movimientos recientes (últimos 30 días)
        fecha_limite = timezone.now().date() - timedelta(days=30)
        movimientos_recientes = MovimientoInventario.objects.filter(
            fecha__gte=fecha_limite
        ).count()
        
        return Response({
            'stock_bajo': stock_bajo_data,
            'total_productos': Producto.objects.filter(activo=True).count(),
            'movimientos_30_dias': movimientos_recientes,
            'almacenes_activos': Stock.objects.values('almacen').distinct().count()
        })

class ReporteFinancieroView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Reporte financiero básico"""
        # Estado de resultados simplificado
        ingresos = FacturaEncabezado.objects.filter(estado='E').aggregate(
            total=Sum('subtotal')  # Sin impuestos
        )['total'] or 0
        
        gastos_compras = OrdenCompra.objects.filter(estado='C').aggregate(
            total=Sum('subtotal')
        )['total'] or 0
        
        gastos_nomina = NominaEncabezado.objects.aggregate(
            total=Sum('neto_a_pagar')
        )['total'] or 0
        
        utilidad_bruta = ingresos - gastos_compras
        utilidad_neta = utilidad_bruta - gastos_nomina
        
        return Response({
            'estado_resultados': {
                'ingresos': float(ingresos),
                'costo_ventas': float(gastos_compras),
                'utilidad_bruta': float(utilidad_bruta),
                'gastos_operativos': float(gastos_nomina),
                'utilidad_neta': float(utilidad_neta)
            },
            'margenes': {
                'margen_bruto': (utilidad_bruta / ingresos * 100) if ingresos > 0 else 0,
                'margen_neto': (utilidad_neta / ingresos * 100) if ingresos > 0 else 0
            }
        })