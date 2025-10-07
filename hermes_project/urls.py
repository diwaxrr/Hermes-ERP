# Archivo: hermes_project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from central.views import (ProductoViewSet, EntidadComercialViewSet, MonedaViewSet,
    TransaccionEncabezadoViewSet,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from inventario.views import (
    AlmacenViewSet, StockViewSet, MovimientoInventarioViewSet,
)
from facturacion.views import FacturaViewSet, PagoViewSet
from compras.views import OrdenCompraViewSet, RecepcionCompraViewSet
from nomina.views import (
    EmpleadoViewSet, ConceptoNominaViewSet, 
    PeriodoNominaViewSet, NominaEncabezadoViewSet
)
from reportes.urls import urlpatterns as reportes_urls
from central.views import home


# Creamos un router para manejar las rutas de la API de forma automática
router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'entidades', EntidadComercialViewSet)
router.register(r'monedas', MonedaViewSet)
router.register(r'transacciones', TransaccionEncabezadoViewSet)

# FACTURACION
router.register(r'facturacion/facturas', FacturaViewSet)
router.register(r'facturacion/pagos', PagoViewSet)

# REGISTRO DE VISTAS DEL MÓDULO INVENTARIO
router.register(r'inventario/almacenes', AlmacenViewSet)
router.register(r'inventario/stock', StockViewSet)
router.register(r'inventario/movimientos', MovimientoInventarioViewSet) # <-- ¡La clave!

# COMPRAS
router.register(r'compras/ordenes', OrdenCompraViewSet)
router.register(r'compras/recepciones', RecepcionCompraViewSet)

# NÓMINA
router.register(r'nomina/empleados', EmpleadoViewSet)
router.register(r'nomina/conceptos', ConceptoNominaViewSet)
router.register(r'nomina/periodos', PeriodoNominaViewSet)
router.register(r'nomina/nominas', NominaEncabezadoViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/reportes/', include(reportes_urls)),
    
    # Rutas de Documentación OpenAPI/Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # UI de la documentación (visualmente agradable)
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]