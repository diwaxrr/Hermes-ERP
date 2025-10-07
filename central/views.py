# Archivo: central/views.py (Reemplazar la sección de 'permission_classes')

from rest_framework import viewsets
from .models import Producto, EntidadComercial, Moneda, TransaccionEncabezado
from .serializers import ProductoSerializer, EntidadComercialSerializer, MonedaSerializer, TransaccionEncabezadoSerializer
from central.permissions import IsContabilidadUser, IsInventarioUser # <-- NUEVA IMPORTACIÓN
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
        <h1>🚀 ERP Hermes - Sistema en Funcionamiento</h1>
        <p><a href="/admin/">Administración</a> | <a href="/api/schema/swagger-ui/">API Docs</a></p>
    """)

# 1. ProductoViewSet (Maestro de Inventario)

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def get_permissions(self):
        # Contabilidad puede VER productos pero no MODIFICARLOS
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]  # Cualquier usuario autenticado puede ver
        else:
            permission_classes = [IsInventarioUser]  # Solo inventario puede crear/editar/eliminar
        return [permission() for permission in permission_classes] 

# 2. EntidadComercialViewSet (Maestro de Clientes/Proveedores)
class EntidadComercialViewSet(viewsets.ModelViewSet):
    queryset = EntidadComercial.objects.all()
    serializer_class = EntidadComercialSerializer
    # Usaremos el mismo permiso, ya que la gestión de clientes suele ser compartida.
    permission_classes = [IsInventarioUser] 

# 3. MonedaViewSet (Maestro Crítico)
class MonedaViewSet(viewsets.ModelViewSet):
    queryset = Moneda.objects.all()
    serializer_class = MonedaSerializer
    # Solo el Superusuario o el Admin (el staff) debería poder cambiar la moneda principal.
    permission_classes = [IsAdminUser] 

# 4. TransaccionEncabezadoViewSet (Motor Contable Crítico)
class TransaccionEncabezadoViewSet(viewsets.ModelViewSet):
    queryset = TransaccionEncabezado.objects.all()
    serializer_class = TransaccionEncabezadoSerializer
    # Solo los usuarios del grupo 'Contabilidad' pueden crear asientos.
    permission_classes = [IsContabilidadUser]