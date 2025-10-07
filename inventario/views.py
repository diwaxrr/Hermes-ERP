# Archivo: inventario/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Almacen, Stock, MovimientoInventario
from .serializers import AlmacenSerializer, StockSerializer, MovimientoInventarioSerializer
# Importamos permisos del núcleo
from central.permissions import IsInventarioUser 

# 1. Almacen ViewSet
class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [IsInventarioUser]

# 2. Stock ViewSet (Lista las existencias actuales)
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsInventarioUser]

# 3. MovimientoInventario ViewSet (CRUD de los movimientos)
class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsInventarioUser]