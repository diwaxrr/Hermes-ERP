# Archivo: central/serializers.py

from rest_framework import serializers
from .models import (Producto, EntidadComercial, Moneda,
    TransaccionEncabezado, MovimientoContable, CuentaContable,
)

# Serializador para Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        # Exponemos todos los campos del modelo Producto
        fields = '__all__' 

# Serializador para EntidadComercial (Cliente/Proveedor)
class EntidadComercialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntidadComercial
        fields = '__all__'

# Serializador para Moneda (necesario para la base de datos)
class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = '__all__'


# Archivo: central/serializers.py (Continuación)

# Serializador para el DETALLE del asiento (MovimientoContable)
class MovimientoContableSerializer(serializers.ModelSerializer):
    # Campo de solo lectura para mostrar el nombre de la cuenta en la respuesta
    cuenta_nombre = serializers.ReadOnlyField(source='cuenta.nombre')

    class Meta:
        model = MovimientoContable
        fields = ['cuenta', 'cuenta_nombre', 'tipo_movimiento', 'monto']
        # Hace que el campo 'encabezado' se maneje automáticamente por el padre
        extra_kwargs = {'encabezado': {'required': False}}


# Serializador para el ENCABEZADO del asiento (TransaccionEncabezado)
class TransaccionEncabezadoSerializer(serializers.ModelSerializer):
    # Campo anidado: permite recibir una lista de movimientos al crear el encabezado
    movimientos = MovimientoContableSerializer(many=True)

    class Meta:
        model = TransaccionEncabezado
        fields = '__all__' # Incluye todos los campos del encabezado + 'movimientos'
    
    # --- Lógica de Validación Crítica ---
    def validate(self, data):
        """
        Verifica que la suma de los Débitos sea igual a la suma de los Créditos.
        """
        movimientos_data = data.get('movimientos')
        if not movimientos_data:
            raise serializers.ValidationError("Una transacción debe tener al menos un movimiento contable (Débito y Crédito).")

        total_debito = sum(m['monto'] for m in movimientos_data if m['tipo_movimiento'] == 'D')
        total_credito = sum(m['monto'] for m in movimientos_data if m['tipo_movimiento'] == 'C')
        
        # Usamos una tolerancia pequeña para evitar errores de coma flotante
        if abs(total_debito - total_credito) > 0.001: 
            raise serializers.ValidationError(
                f"El asiento contable no balancea. Débito Total: {total_debito}, Crédito Total: {total_credito}."
            )

        return data
        
    # --- Lógica de Creación Anidada ---
    def create(self, validated_data):
        movimientos_data = validated_data.pop('movimientos')
        
        # 1. Crear el Encabezado
        transaccion = TransaccionEncabezado.objects.create(**validated_data)
        
        # 2. Crear los Movimientos y asignarlos al Encabezado
        for movimiento_data in movimientos_data:
            MovimientoContable.objects.create(encabezado=transaccion, **movimiento_data)
        
        return transaccion