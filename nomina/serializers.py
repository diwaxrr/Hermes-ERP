# Archivo: nomina/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import Empleado, ConceptoNomina, PeriodoNomina, NominaEncabezado, NominaDetalle
from central.models import CuentaContable, TransaccionEncabezado, MovimientoContable

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'

class ConceptoNominaSerializer(serializers.ModelSerializer):
    cuenta_contable_nombre = serializers.CharField(source='cuenta_contable.nombre', read_only=True)
    
    class Meta:
        model = ConceptoNomina
        fields = '__all__'

class PeriodoNominaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoNomina
        fields = '__all__'

class NominaDetalleSerializer(serializers.ModelSerializer):
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)
    concepto_tipo = serializers.CharField(source='concepto.tipo', read_only=True)
    
    class Meta:
        model = NominaDetalle
        fields = ['id', 'concepto', 'concepto_nombre', 'concepto_tipo', 'cantidad', 'valor']

class NominaEncabezadoSerializer(serializers.ModelSerializer):
    detalles = NominaDetalleSerializer(many=True)
    empleado_nombre = serializers.CharField(source='empleado.nombres', read_only=True)
    periodo_descripcion = serializers.CharField(source='periodo.descripcion', read_only=True)
    
    class Meta:
        model = NominaEncabezado
        fields = [
            'id', 'empleado', 'empleado_nombre', 'periodo', 'periodo_descripcion',
            'total_devengos', 'total_deducciones', 'neto_a_pagar', 
            'asiento_contable', 'detalles'
        ]
        read_only_fields = ['total_devengos', 'total_deducciones', 'neto_a_pagar', 'asiento_contable']
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        with transaction.atomic():
            # Crear encabezado de nómina
            nomina = NominaEncabezado.objects.create(**validated_data)
            
            # Procesar detalles y calcular totales
            total_devengos = 0
            total_deducciones = 0
            
            for detalle_data in detalles_data:
                concepto = detalle_data['concepto']
                valor = detalle_data['valor']
                
                # Crear detalle
                NominaDetalle.objects.create(
                    nomina=nomina,
                    concepto=concepto,
                    cantidad=detalle_data.get('cantidad', 1),
                    valor=valor
                )
                
                # Acumular por tipo
                if concepto.tipo == 'D':  # Devengo
                    total_devengos += valor
                elif concepto.tipo == 'C':  # Deducción
                    total_deducciones += valor
            
            # Calcular neto a pagar
            neto_a_pagar = total_devengos - total_deducciones
            
            # Actualizar nómina con totales
            nomina.total_devengos = total_devengos
            nomina.total_deducciones = total_deducciones
            nomina.neto_a_pagar = neto_a_pagar
            nomina.save()
            
            # Generar asiento contable automático
            self.crear_asiento_contable(nomina)
            
            return nomina
    
    def crear_asiento_contable(self, nomina):
        """Crea el asiento contable automáticamente para la nómina"""
        try:
            # Buscar cuentas contables (ajustar según tu plan contable)
            cuenta_nomina = CuentaContable.objects.get(codigo='510505')  # Gastos de nómina
            cuenta_provisiones = CuentaContable.objects.get(codigo='260505')  # Provisiones
            cuenta_por_pagar = CuentaContable.objects.get(codigo='210505')  # Nómina por pagar
            
            # Usar moneda principal
            from central.models import Moneda
            moneda_principal = Moneda.objects.get(es_principal=True)
            
            # Crear encabezado del asiento
            asiento = TransaccionEncabezado.objects.create(
                fecha=nomina.periodo.fecha_pago,
                referencia=f"NOM-{nomina.empleado.cedula}-{nomina.periodo.descripcion}",
                descripcion=f"Nómina {nomina.empleado.nombres} {nomina.periodo.descripcion}",
                entidad=None,  # No aplica a entidad comercial
                moneda=moneda_principal,
                tasa_cambio=1.0
            )
            
            # Movimiento 1: Débito a Gastos de Nómina (total devengos)
            MovimientoContable.objects.create(
                encabezado=asiento,
                cuenta=cuenta_nomina,
                tipo_movimiento='D',
                monto=nomina.total_devengos
            )
            
            # Movimiento 2: Crédito a Nómina por Pagar (neto a pagar)
            MovimientoContable.objects.create(
                encabezado=asiento,
                cuenta=cuenta_por_pagar,
                tipo_movimiento='C',
                monto=nomina.neto_a_pagar
            )
            
            # Movimiento 3: Crédito a Provisiones (deducciones)
            if nomina.total_deducciones > 0:
                MovimientoContable.objects.create(
                    encabezado=asiento,
                    cuenta=cuenta_provisiones,
                    tipo_movimiento='C',
                    monto=nomina.total_deducciones
                )
            
            # Enlazar asiento con nómina
            nomina.asiento_contable = asiento
            nomina.save()
            
        except (CuentaContable.DoesNotExist, Moneda.DoesNotExist) as e:
            # En producción, esto debería manejarse mejor
            print(f"ERROR: Configuración contable no encontrada: {e}")