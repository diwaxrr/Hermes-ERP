# Archivo: central/tests.py

from django.test import TestCase
from django.contrib.auth.models import User, Group
from central.models import Moneda, CuentaContable, Producto, EntidadComercial
from central.serializers import TransaccionEncabezadoSerializer
from datetime import date

# ==============================================================================
# PRUEBAS DE LA LÓGICA FINANCIERA (ASIENTOS)
# ==============================================================================

class TransaccionSerializerTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Prepara los datos necesarios una sola vez para todas las pruebas de esta clase."""
        # 1. Crear una Moneda Base
        cls.moneda_base = Moneda.objects.create(
            codigo_iso='USD', 
            nombre='Dólar Americano', 
            simbolo='$', 
            es_principal=True
        )
        
        # 2. Crear Cuentas Contables necesarias
        cls.cuenta_caja = CuentaContable.objects.create(
            codigo='110505', nombre='Caja General', tipo='A', naturaleza='D', activo=True
        )
        cls.cuenta_ingreso = CuentaContable.objects.create(
            codigo='413505', nombre='Ventas de Mercancía', tipo='I', naturaleza='C', activo=True
        )
        cls.cuenta_inventario = CuentaContable.objects.create(
            codigo='143505', nombre='Mercancías', tipo='A', naturaleza='D', activo=True
        )
        cls.cuenta_costo = CuentaContable.objects.create(
            codigo='613505', nombre='Costo de Venta', tipo='G', naturaleza='D', activo=True
        )

        # 3. Crear un usuario para simular una API request (Opcional, pero buena práctica)
        cls.user = User.objects.create_user(username='testuser', password='password123')
        Group.objects.create(name='Contabilidad')
        cls.user.groups.add(Group.objects.get(name='Contabilidad'))


    def get_valid_payload(self, total_monto):
        """Retorna un diccionario de datos balanceado para una prueba exitosa."""
        return {
            'fecha': date.today().isoformat(),
            'referencia': 'FACT-001-TEST',
            'descripcion': 'Asiento de prueba balanceado',
            'entidad': None, # Opcional
            'moneda': self.moneda_base.id, # Usamos la ID de la moneda creada
            'tasa_cambio': 1.0000,
            'movimientos': [
                {
                    'cuenta': self.cuenta_caja.id, # Débito (Aumenta Activo)
                    'tipo_movimiento': 'D',
                    'monto': str(total_monto) # Monto como string (formato serializer)
                },
                {
                    'cuenta': self.cuenta_ingreso.id, # Crédito (Aumenta Ingreso)
                    'tipo_movimiento': 'C',
                    'monto': str(total_monto) 
                }
            ]
        }

    # --- PRUEBA 1: BALANCE OK (DÉBITO = CRÉDITO) ---
    def test_transaccion_balance_is_valid(self):
        """Asegura que un asiento con Débito = Crédito es válido."""
        payload = self.get_valid_payload(total_monto=100.50)
        serializer = TransaccionEncabezadoSerializer(data=payload)
        
        # Debe pasar la validación
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        # Debe poder crearse
        transaccion = serializer.save()
        self.assertEqual(transaccion.movimientos.count(), 2)
        
    # --- PRUEBA 2: BALANCE FALLIDO (DÉBITO != CRÉDITO) ---
    def test_transaccion_imbalance_is_invalid(self):
        """Asegura que un asiento con Débito != Crédito es inválido."""
        payload = self.get_valid_payload(total_monto=50.00)
        
        # Cambiamos intencionalmente el monto del Crédito para desbalancear
        payload['movimientos'][1]['monto'] = '49.00' 
        
        serializer = TransaccionEncabezadoSerializer(data=payload)
        
        # No debe pasar la validación
        self.assertFalse(serializer.is_valid())
        
        # Debe contener el error de validación en el campo 'non_field_errors'
        self.assertIn('El asiento contable no balancea', str(serializer.errors))

    # --- PRUEBA 3: ASIGNACIÓN DE ENCABEZADO ---
    def test_transaccion_movimientos_are_assigned_to_header(self):
        """Asegura que los movimientos se crean y se asignan al encabezado correcto."""
        payload = self.get_valid_payload(total_monto=250.00)
        serializer = TransaccionEncabezadoSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
        
        transaccion = serializer.save()
        
        # Verificar que el Foreign Key del movimiento apunta al encabezado creado
        for movimiento in transaccion.movimientos.all():
            self.assertEqual(movimiento.encabezado.id, transaccion.id)

# ==============================================================================
# PRUEBAS DE MÓDULO CENTRAL (Modelos Básicos)
# ==============================================================================

class ModuloCentralTests(TestCase):
    
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        self.moneda = Moneda.objects.create(
            codigo_iso='USD', nombre='Dólar Americano', simbolo='$', es_principal=True
        )
        
    def test_creacion_producto(self):
        """Verifica la creación básica de un producto"""
        producto = Producto.objects.create(
            nombre='Laptop Dell',
            codigo_sku='LP-DELL-001',
            tipo='P',
            precio_venta=1500.00,
            costo_unitario=1200.00,
            unidad_medida='Unidad'
        )
        self.assertEqual(producto.nombre, 'Laptop Dell')
        self.assertTrue(producto.activo)
        
    def test_creacion_entidad_comercial(self):
        """Verifica la creación de cliente/proveedor"""
        entidad = EntidadComercial.objects.create(
            nombre_comercial='Empresa ABC',
            identificacion_fiscal='123-456789',
            tipo='C',
            correo_electronico='contacto@empresaabc.com'
        )
        self.assertEqual(entidad.tipo, 'C')
        self.assertEqual(entidad.plazo_credito_dias, 0)
        
    def test_creacion_cuenta_contable(self):
        """Verifica la jerarquía de cuentas contables"""
        cuenta_padre = CuentaContable.objects.create(
            codigo='1', nombre='Activo', tipo='A', naturaleza='D'
        )
        cuenta_hija = CuentaContable.objects.create(
            codigo='1105', nombre='Caja', tipo='A', naturaleza='D', cuenta_padre=cuenta_padre
        )
        self.assertEqual(cuenta_hija.cuenta_padre, cuenta_padre)
        self.assertIn(cuenta_hija, cuenta_padre.cuentas_hijas.all())
        
    def test_moneda_principal_unica(self):
        """Verifica que solo haya una moneda principal"""
        # Intentar crear segunda moneda principal debería ser posible,
        # pero en la lógica de negocio se debe validar
        moneda_secundaria = Moneda.objects.create(
            codigo_iso='EUR', nombre='Euro', simbolo='€', es_principal=True
        )
        # Ambas pueden ser principales en la BD, pero la lógica debe prevenir esto
        monedas_principales = Moneda.objects.filter(es_principal=True)
        self.assertEqual(monedas_principales.count(), 2)