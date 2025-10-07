# Archivo: inventario/tests.py

from django.test import TestCase
from django.contrib.auth.models import User, Group
from inventario.models import Almacen, MovimientoInventario
from inventario.serializers import MovimientoInventarioSerializer
from central.models import Producto, Moneda, CuentaContable

class IntegracionInventarioContabilidadTest(TestCase):
    
    def setUp(self):
        # Configurar datos de prueba
        self.moneda = Moneda.objects.create(
            codigo_iso='USD', nombre='Dólar', simbolo='$', es_principal=True
        )
        self.cuenta_costo = CuentaContable.objects.create(
            codigo='613505', nombre='Costo de Venta', tipo='G', naturaleza='D'
        )
        self.cuenta_inventario = CuentaContable.objects.create(
            codigo='143505', nombre='Inventario', tipo='A', naturaleza='D'
        )
        self.producto = Producto.objects.create(
            nombre='Producto Test', codigo_sku='TEST-001', 
            precio_venta=100, costo_unitario=50, unidad_medida='Unidad'
        )
        self.almacen = Almacen.objects.create(
            nombre='Almacén Test', codigo='ALM-TEST'
        )

    def test_salida_inventario_genera_asiento_contable(self):
        """Verifica que una salida de inventario genere automáticamente un asiento contable"""
        # Usar el serializer para crear el movimiento (que es lo que dispara la creación del asiento)
        serializer = MovimientoInventarioSerializer(data={
            'tipo_movimiento': 'S',
            'producto': self.producto.id,
            'almacen': self.almacen.id,
            'cantidad': 2,
            'referencia_doc': 'TEST-SALIDA-001'
        })
        
        self.assertTrue(serializer.is_valid())
        movimiento = serializer.save()
        
        # Verificar que se creó el asiento contable
        self.assertIsNotNone(movimiento.asiento_contable_nucleo)
        
        # Verificar que el asiento tiene 2 movimientos (Débito y Crédito)
        asiento = movimiento.asiento_contable_nucleo
        self.assertEqual(asiento.movimientos.count(), 2)
        
        # Verificar montos
        movimiento_debito = asiento.movimientos.get(tipo_movimiento='D')
        movimiento_credito = asiento.movimientos.get(tipo_movimiento='C')
        
        costo_esperado = 2 * 50  # cantidad * costo_unitario
        self.assertEqual(movimiento_debito.monto, costo_esperado)
        self.assertEqual(movimiento_credito.monto, costo_esperado)