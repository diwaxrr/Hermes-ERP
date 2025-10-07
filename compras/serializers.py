# Archivo: compras/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import OrdenCompra, OrdenCompraDetalle, RecepcionCompra
from central.models import CuentaContable, TransaccionEncabezado, MovimientoContable
from inventario.models import MovimientoInventario, Almacen

class OrdenCompraDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = OrdenCompraDetalle
        fields = [
            'id', 'producto', 'producto_nombre', 'cantidad_solicitada', 
            'cantidad_recibida', 'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['cantidad_recibida', 'subtotal']

class OrdenCompraSerializer(serializers.ModelSerializer):
    detalles = OrdenCompraDetalleSerializer(many=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    
    class Meta:
        model = OrdenCompra
        fields = [
            'id', 'numero_orden', 'fecha_emision', 'fecha_esperada',
            'proveedor', 'proveedor_nombre', 'moneda', 'subtotal', 
            'impuesto', 'total', 'estado', 'detalles'
        ]
        read_only_fields = ['subtotal', 'impuesto', 'total']
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        with transaction.atomic():
            # Crear orden de compra
            orden_compra = OrdenCompra.objects.create(**validated_data)
            
            # Crear detalles y calcular totales
            total_subtotal = 0
            for detalle_data in detalles_data:
                cantidad = detalle_data['cantidad_solicitada']
                precio_unitario = detalle_data['precio_unitario']
                
                # Calcular subtotal de línea
                subtotal_linea = cantidad * precio_unitario
                total_subtotal += subtotal_linea
                
                # Crear detalle
                OrdenCompraDetalle.objects.create(
                    orden_compra=orden_compra,
                    producto=detalle_data['producto'],
                    cantidad_solicitada=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal_linea
                )
            
            # Calcular impuestos y total
            impuesto = total_subtotal * 0.18  # 18% IVA - ajustar según configuración
            total = total_subtotal + impuesto
            
            # Actualizar orden con totales
            orden_compra.subtotal = total_subtotal
            orden_compra.impuesto = impuesto
            orden_compra.total = total
            orden_compra.save()
            
            return orden_compra

class RecepcionCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecepcionCompra
        fields = '__all__'
        read_only_fields = ['movimiento_inventario']
    
    def create(self, validated_data):
        with transaction.atomic():
            recepcion = RecepcionCompra.objects.create(**validated_data)
            
            # Aquí irá la lógica para:
            # 1. Actualizar cantidad_recibida en OrdenCompraDetalle
            # 2. Crear movimiento de inventario de entrada
            # 3. Actualizar estado de la orden de compra
            # 4. Generar asiento contable si es necesario
            
            return recepcion