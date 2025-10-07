# Archivo: compras/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OrdenCompra, RecepcionCompra
from .serializers import OrdenCompraSerializer, RecepcionCompraSerializer
from central.permissions import IsInventarioUser

class OrdenCompraViewSet(viewsets.ModelViewSet):
    queryset = OrdenCompra.objects.all()
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsInventarioUser]  # Inventario gestiona compras
    
    @action(detail=True, methods=['post'])
    def recibir(self, request, pk=None):
        """Recibir mercancía contra una orden de compra"""
        orden_compra = self.get_object()
        
        # Aquí irá la lógica completa de recepción
        # Por ahora solo marcamos como recibida
        if orden_compra.estado in ['E', 'R']:  # Emitida o Recibida parcialmente
            orden_compra.estado = 'R'  # Recibida parcialmente
            orden_compra.save()
            
            # TODO: Lógica para:
            # 1. Crear RecepcionCompra
            # 2. Actualizar cantidades recibidas
            # 3. Crear movimiento de inventario
            # 4. Generar asiento contable
            
            return Response({'status': 'Recepción iniciada - funcionalidad en desarrollo'})
        
        return Response(
            {'error': 'Solo se pueden recibir órdenes emitidas'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class RecepcionCompraViewSet(viewsets.ModelViewSet):
    queryset = RecepcionCompra.objects.all()
    serializer_class = RecepcionCompraSerializer
    permission_classes = [IsInventarioUser]