# Archivo: facturacion/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import FacturaEncabezado, FacturaDetalle, Pago
from central.models import CuentaContable, TransaccionEncabezado, MovimientoContable
from inventario.models import MovimientoInventario

class FacturaDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = FacturaDetalle
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['subtotal']

class FacturaEncabezadoSerializer(serializers.ModelSerializer):
    detalles = FacturaDetalleSerializer(many=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre_comercial', read_only=True)
    
    class Meta:
        model = FacturaEncabezado
        fields = [
            'id', 'numero_factura', 'fecha_emision', 'fecha_vencimiento',
            'cliente', 'cliente_nombre', 'moneda', 'subtotal', 'impuesto', 
            'total', 'estado', 'detalles', 'asiento_contable'
        ]
        read_only_fields = ['subtotal', 'impuesto', 'total', 'asiento_contable']
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        with transaction.atomic():
            # Crear factura
            factura = FacturaEncabezado.objects.create(**validated_data)
            
            # Crear detalles y calcular totales
            total_subtotal = 0
            for detalle_data in detalles_data:
                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']
                precio_unitario = detalle_data['precio_unitario']
                
                # Calcular subtotal de línea
                subtotal_linea = cantidad * precio_unitario
                total_subtotal += subtotal_linea
                
                # Crear detalle
                FacturaDetalle.objects.create(
                    factura=factura,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal_linea
                )
                
                # Si es producto físico, generar salida de inventario
                if producto.tipo == 'P':  # Producto Físico
                    MovimientoInventario.objects.create(
                        tipo_movimiento='S',  # Salida
                        producto=producto,
                        almacen_id=1,  # Almacén principal - ajustar según necesidad
                        cantidad=cantidad,
                        referencia_doc=f"FACT-{factura.numero_factura}"
                    )
            
            # Calcular impuestos y total
            impuesto = total_subtotal * 0.18  # 18% IVA - ajustar según configuración
            total = total_subtotal + impuesto
            
            # Actualizar factura con totales
            factura.subtotal = total_subtotal
            factura.impuesto = impuesto
            factura.total = total
            factura.save()
            
            # Generar asiento contable automático
            self.crear_asiento_contable(factura)
            
            return factura
    
    def crear_asiento_contable(self, factura):
        """Crea el asiento contable automáticamente para la factura"""
        try:
            # Buscar cuentas contables (ajustar códigos según tu plan contable)
            cuenta_ingresos = CuentaContable.objects.get(codigo='413505')  # Ventas
            cuenta_iva = CuentaContable.objects.get(codigo='240805')       # IVA por cobrar
            cuenta_clientes = CuentaContable.objects.get(codigo='130505')  # Clientes
            
            # Crear encabezado del asiento
            asiento = TransaccionEncabezado.objects.create(
                fecha=factura.fecha_emision,
                referencia=f"FACT-{factura.numero_factura}",
                descripcion=f"Facturación a {factura.cliente.nombre_comercial}",
                entidad=factura.cliente,
                moneda=factura.moneda,
                tasa_cambio=1.0
            )
            
            # Movimientos contables
            # Débito: Clientes (Activo - aumenta)
            MovimientoContable.objects.create(
                encabezado=asiento,
                cuenta=cuenta_clientes,
                tipo_movimiento='D',
                monto=factura.total
            )
            
            # Crédito: Ingresos por ventas (Ingreso - aumenta)
            MovimientoContable.objects.create(
                encabezado=asiento,
                cuenta=cuenta_ingresos,
                tipo_movimiento='C',
                monto=factura.subtotal
            )
            
            # Crédito: IVA por cobrar (Pasivo - aumenta)
            MovimientoContable.objects.create(
                encabezado=asiento,
                cuenta=cuenta_iva,
                tipo_movimiento='C',
                monto=factura.impuesto
            )
            
            # Enlazar asiento con factura
            factura.asiento_contable = asiento
            factura.save()
            
        except CuentaContable.DoesNotExist as e:
            # En producción, esto debería manejarse mejor
            print(f"ERROR: Cuenta contable no encontrada: {e}")

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'
        read_only_fields = ['asiento_contable']