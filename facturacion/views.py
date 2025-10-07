# Archivo: facturacion/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FacturaEncabezado, Pago
from .serializers import FacturaEncabezadoSerializer, PagoSerializer
from central.permissions import IsContabilidadUser

class FacturaViewSet(viewsets.ModelViewSet):
    queryset = FacturaEncabezado.objects.all()
    serializer_class = FacturaEncabezadoSerializer
    permission_classes = [IsContabilidadUser]  # Solo contabilidad puede facturar
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anular una factura"""
        factura = self.get_object()
        if factura.estado == 'E':  # Solo se puede anular facturas emitidas
            factura.estado = 'A'
            factura.save()
            # Aquí se podría revertir el asiento contable y el movimiento de inventario
            return Response({'status': 'Factura anulada'})
        return Response(
            {'error': 'Solo se pueden anular facturas emitidas'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [IsContabilidadUser]