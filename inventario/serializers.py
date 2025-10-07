from rest_framework import serializers
from django.db import transaction
from .models import Almacen, Stock, MovimientoInventario
# Importamos modelos del Núcleo que vamos a usar para la contabilidad
from central.models import CuentaContable, Moneda, TransaccionEncabezado, MovimientoContable


class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)
    
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['producto', 'almacen', 'cantidad']


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        fields = '__all__'
        read_only_fields = ['asiento_contable_nucleo']

    def create(self, validated_data):
        with transaction.atomic():
            movimiento = MovimientoInventario.objects.create(**validated_data)

            # Solo para SALIDAS ('S') se registra Costo de Venta
            if movimiento.tipo_movimiento == 'S':
                try:
                    # ✅ Corregido: usar 'es_principal'
                    moneda_base = Moneda.objects.get(es_principal=True)
                    cuenta_costo = CuentaContable.objects.get(codigo='613505')
                    cuenta_inventario = CuentaContable.objects.get(codigo='143505')
                except Moneda.DoesNotExist:
                    raise serializers.ValidationError(
                        "ERROR DE CONFIGURACIÓN: No hay una moneda marcada como principal (es_principal=True)."
                    )
                except CuentaContable.DoesNotExist as e:
                    # Mejor manejo del error
                    raise serializers.ValidationError(
                        "ERROR DE CONFIGURACIÓN: Faltan cuentas contables críticas (613505 para Costo de Venta o 143505 para Inventario)."
                    )

                # Verificar que el producto tenga costo_unitario
                if movimiento.producto.costo_unitario is None:
                    raise serializers.ValidationError(
                        f"El producto '{movimiento.producto.nombre}' no tiene costo unitario definido. No se puede registrar el costo de venta."
                    )

                costo_total = movimiento.producto.costo_unitario * movimiento.cantidad

                # ✅ Corregido: eliminar 'tipo_transaccion' (campo inexistente)
                asiento_encabezado = TransaccionEncabezado.objects.create(
                    fecha=movimiento.fecha,
                    moneda=moneda_base,
                    referencia=f"Costo-Venta-{movimiento.referencia_doc}-{movimiento.id}",
                    descripcion=f"Registro automático de costo de venta para {movimiento.referencia_doc}",
                    entidad=None  # Opcional, puedes dejarlo None
                )

                # Crear los movimientos contables
                MovimientoContable.objects.create(
                    encabezado=asiento_encabezado,  # ✅ 'encabezado', no 'transaccion_encabezado'
                    cuenta=cuenta_costo,            # ✅ 'cuenta', no 'cuenta_contable'
                    tipo_movimiento='D',
                    monto=costo_total
                )
                MovimientoContable.objects.create(
                    encabezado=asiento_encabezado,
                    cuenta=cuenta_inventario,
                    tipo_movimiento='C',
                    monto=costo_total
                )

                # Enlazar el asiento al movimiento de inventario
                movimiento.asiento_contable_nucleo = asiento_encabezado
                movimiento.save()

            return movimiento