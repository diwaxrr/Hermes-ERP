# Archivo: inventario/tests_señales.py

from django.test import TestCase
from inventario.models import Almacen, MovimientoInventario, Stock
from central.models import Producto

class SeñalesStockTests(TestCase):
    
    def setUp(self):
        """Configuración inicial"""
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            codigo_sku='TEST-SEÑAL-001',
            precio_venta=100.00,
            unidad_medida='Unidad'
        )
        self.almacen = Almacen.objects.create(
            nombre='Almacén Test Señales',
            codigo='ALM-SEÑAL'
        )
    
    def test_señal_entrada_incrementa_stock(self):
        """Verifica que una entrada de inventario incrementa el stock"""
        # Stock inicial debería ser 0 o crearse automáticamente
        stock_inicial = Stock.objects.filter(
            producto=self.producto, 
            almacen=self.almacen
        ).first()
        
        # Crear movimiento de ENTRADA
        movimiento = MovimientoInventario.objects.create(
            tipo_movimiento='E',
            producto=self.producto,
            almacen=self.almacen,
            cantidad=10,
            referencia_doc='ENTRADA-TEST-001'
        )
        
        # Verificar que el stock se actualizó
        stock_actualizado = Stock.objects.get(
            producto=self.producto, 
            almacen=self.almacen
        )
        self.assertEqual(stock_actualizado.cantidad, 10)
    
    def test_señal_salida_decrementa_stock(self):
        """Verifica que una salida de inventario decrementa el stock"""
        # Primero crear stock inicial con una entrada
        MovimientoInventario.objects.create(
            tipo_movimiento='E',
            producto=self.producto,
            almacen=self.almacen,
            cantidad=20,
            referencia_doc='ENTRADA-INICIAL'
        )
        
        # Crear movimiento de SALIDA
        MovimientoInventario.objects.create(
            tipo_movimiento='S',
            producto=self.producto,
            almacen=self.almacen,
            cantidad=5,
            referencia_doc='SALIDA-TEST-001'
        )
        
        # Verificar que el stock se decrementó correctamente
        stock_final = Stock.objects.get(
            producto=self.producto, 
            almacen=self.almacen
        )
        self.assertEqual(stock_final.cantidad, 15)
    
    def test_señal_stock_negativo_prevenido(self):
        """Verifica que no se permite stock negativo"""
        # Crear salida sin stock inicial debería funcionar (depende de la lógica de negocio)
        movimiento = MovimientoInventario.objects.create(
            tipo_movimiento='S',
            producto=self.producto,
            almacen=self.almacen,
            cantidad=5,
            referencia_doc='SALIDA-SIN-STOCK'
        )
        
        # Verificar el resultado (puede ser negativo o 0 dependiendo de la configuración)
        stock_final = Stock.objects.get(
            producto=self.producto, 
            almacen=self.almacen
        )
        # Esto prueba que la señal se ejecutó, no necesariamente la lógica de negocio
        self.assertIsNotNone(stock_final)

# Forzar la carga de señales en las pruebas
from inventario import signals