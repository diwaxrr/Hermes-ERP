# Archivo: central/tests_api.py

from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from central.models import Producto, EntidadComercial, Moneda, CuentaContable

class APIEndpointsTests(APITestCase):
    
    def setUp(self):
        """Configuración inicial para todas las pruebas de API"""
        # Crear usuarios y grupos
        self.user_inventario = User.objects.create_user(username='inventario_user', password='test123')
        self.user_contabilidad = User.objects.create_user(username='contabilidad_user', password='test123')
        self.user_admin = User.objects.create_user(username='admin_user', password='test123', is_staff=True)
        
        Group.objects.create(name='Inventario')
        Group.objects.create(name='Contabilidad')
        
        self.user_inventario.groups.add(Group.objects.get(name='Inventario'))
        self.user_contabilidad.groups.add(Group.objects.get(name='Contabilidad'))
        
        # Crear datos de prueba
        self.moneda = Moneda.objects.create(
            codigo_iso='USD', nombre='Dólar Americano', simbolo='$', es_principal=True
        )
        
        self.producto = Producto.objects.create(
            nombre='Laptop Test',
            codigo_sku='LP-TEST-001',
            precio_venta=1500.00,
            unidad_medida='Unidad'
        )
        
        self.entidad = EntidadComercial.objects.create(
            nombre_comercial='Cliente Test',
            identificacion_fiscal='123-456789',
            tipo='C'
        )
        
        self.cuenta_contable = CuentaContable.objects.create(
            codigo='110505', nombre='Caja General', tipo='A', naturaleza='D'
        )

    # ==========================================================================
    # PRUEBAS DE PRODUCTOS
    # ==========================================================================
    
    def test_api_productos_list(self):
        """Verifica que se puede listar productos"""
        self.client.force_authenticate(user=self.user_inventario)
        response = self.client.get('/api/productos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Paginación activa
    
    def test_api_productos_create(self):
        """Verifica que usuario inventario puede crear productos"""
        self.client.force_authenticate(user=self.user_inventario)
        data = {
            'nombre': 'Nuevo Producto',
            'codigo_sku': 'NEW-001',
            'precio_venta': 100.00,
            'unidad_medida': 'Unidad'
        }
        response = self.client.post('/api/productos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 2)
    
    def test_api_productos_contabilidad_no_access(self):
        """Verifica que usuario contabilidad NO puede crear productos"""
        self.client.force_authenticate(user=self.user_contabilidad)
        data = {
            'nombre': 'Producto Bloqueado',
            'codigo_sku': 'BLOCK-001',
            'precio_venta': 50.00,
            'unidad_medida': 'Unidad'
        }
        response = self.client.post('/api/productos/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==========================================================================
    # PRUEBAS DE ENTIDADES COMERCIALES
    # ==========================================================================
    
    def test_api_entidades_list(self):
        """Verifica que se puede listar entidades comerciales"""
        self.client.force_authenticate(user=self.user_inventario)
        response = self.client.get('/api/entidades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_entidades_create(self):
        """Verifica creación de entidades comerciales"""
        self.client.force_authenticate(user=self.user_inventario)
        data = {
            'nombre_comercial': 'Nuevo Proveedor',
            'identificacion_fiscal': '987-654321',
            'tipo': 'P',
            'correo_electronico': 'proveedor@test.com'
        }
        response = self.client.post('/api/entidades/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EntidadComercial.objects.count(), 2)

    # ==========================================================================
    # PRUEBAS DE MONEDAS (Solo Admin)
    # ==========================================================================
    
    def test_api_monedas_admin_access(self):
        """Verifica que solo admin puede acceder a monedas"""
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get('/api/monedas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_monedas_inventario_no_access(self):
        """Verifica que usuario inventario NO puede acceder a monedas"""
        self.client.force_authenticate(user=self.user_inventario)
        response = self.client.get('/api/monedas/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==========================================================================
    # PRUEBAS DE DOCUMENTACIÓN SWAGGER
    # ==========================================================================
    
    def test_api_documentacion_swagger(self):
        """Verifica que la documentación Swagger está disponible"""
        response = self.client.get('/api/schema/swagger-ui/')
        # Puede redirigir o dar 200, pero no debería dar error 404/500
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_302_FOUND])
    
    def test_api_esquema_openapi(self):
        """Verifica que el esquema OpenAPI está disponible"""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que contiene elementos básicos de OpenAPI
        self.assertIn('openapi', response.data)
        self.assertIn('paths', response.data)


    # Permisos

    # Archivo: central/tests_api.py

    def test_debug_permisos_usuario(self):
        """Debug: Verificar grupos y permisos del usuario"""
        print(f"Usuario contabilidad grupos: {list(self.user_contabilidad.groups.all())}")
        print(f"Usuario inventario grupos: {list(self.user_inventario.groups.all())}")
        
        # Verificar si el permiso está funcionando
        from central.permissions import IsInventarioUser
        permission = IsInventarioUser()
        has_perm_inventario = permission.has_permission(
            type('Request', (), {'user': self.user_inventario})(), 
            type('View', (), {})()
        )
        has_perm_contabilidad = permission.has_permission(
            type('Request', (), {'user': self.user_contabilidad})(), 
            type('View', (), {})()
        )
        
        print(f"Usuario inventario tiene permiso: {has_perm_inventario}")
        print(f"Usuario contabilidad tiene permiso: {has_perm_contabilidad}")
        
        self.client.force_authenticate(user=self.user_contabilidad)
        response = self.client.get('/api/productos/')
        print(f"Status code productos (contabilidad): {response.status_code}")


        # Permisos otros

    def test_debug_producto_permissions_detail(self):
        """Debug: Verificar permisos específicos por acción"""
        self.client.force_authenticate(user=self.user_contabilidad)
        
        # Probar GET (debería funcionar)
        response_get = self.client.get('/api/productos/')
        print(f"GET /api/productos/ - Status: {response_get.status_code}")
        
        # Probar POST (debería fallar)
        data = {
            'nombre': 'Producto Debug',
            'codigo_sku': 'DEBUG-001',
            'precio_venta': 50.00,
            'unidad_medida': 'Unidad'
        }
        response_post = self.client.post('/api/productos/', data)
        print(f"POST /api/productos/ - Status: {response_post.status_code}")
        
        # Verificar qué acción detecta la vista
        from central.views import ProductoViewSet
        view = ProductoViewSet()
        view.action = 'create'  # Simular acción de creación
        permissions = view.get_permissions()
        print(f"Permisos para acción 'create': {[type(p).__name__ for p in permissions]}")

        # Prueba de debug

        # Archivo: central/tests_api.py

    def test_debug_grupos_detallado(self):
        """Debug detallado de grupos y permisos"""
        print("=== DEBUG DETALLADO DE GRUPOS ===")
        
        # Verificar grupos directamente
        grupos_inventario = list(self.user_inventario.groups.all())
        grupos_contabilidad = list(self.user_contabilidad.groups.all())
        
        print(f"Usuario inventario: {self.user_inventario.username}")
        print(f"Grupos: {[g.name for g in grupos_inventario]}")
        print(f"Tiene grupo 'Inventario': {self.user_inventario.groups.filter(name='Inventario').exists()}")
        
        print(f"Usuario contabilidad: {self.user_contabilidad.username}")  
        print(f"Grupos: {[g.name for g in grupos_contabilidad]}")
        print(f"Tiene grupo 'Inventario': {self.user_contabilidad.groups.filter(name='Inventario').exists()}")
        
        # Verificar el permiso directamente
        from central.permissions import IsInventarioUser
        permission_checker = IsInventarioUser()
        
        # Simular request
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        has_perm_inv = permission_checker.has_permission(MockRequest(self.user_inventario), None)
        has_perm_cont = permission_checker.has_permission(MockRequest(self.user_contabilidad), None)
        
        print(f"Permiso inventario: {has_perm_inv}")
        print(f"Permiso contabilidad: {has_perm_cont}")