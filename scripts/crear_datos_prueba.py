# Archivo: scripts/crear_datos_prueba.py

import os
import django
import random
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hermes_project.settings')
django.setup()

from django.contrib.auth.models import User, Group
from central.models import (
    Producto, EntidadComercial, Moneda, CuentaContable,
    TransaccionEncabezado, MovimientoContable
)
from inventario.models import Almacen, Stock, MovimientoInventario
from facturacion.models import FacturaEncabezado, FacturaDetalle
from compras.models import OrdenCompra, OrdenCompraDetalle
from nomina.models import Empleado, ConceptoNomina, PeriodoNomina

def crear_moneda_principal():
    """Crear moneda principal si no existe"""
    moneda, created = Moneda.objects.get_or_create(
        codigo_iso='DOP',
        defaults={
            'nombre': 'Peso Dominicano',
            'simbolo': 'RD$',
            'es_principal': True
        }
    )
    print(f"✅ Moneda: {moneda.nombre}")
    return moneda

def crear_cuentas_contables():
    """Crear cuentas contables básicas"""
    cuentas = [
        # Activos
        {'codigo': '110505', 'nombre': 'Caja General', 'tipo': 'A', 'naturaleza': 'D'},
        {'codigo': '130505', 'nombre': 'Clientes', 'tipo': 'A', 'naturaleza': 'D'},
        {'codigo': '143505', 'nombre': 'Inventario de Mercancías', 'tipo': 'A', 'naturaleza': 'D'},
        
        # Pasivos
        {'codigo': '210505', 'nombre': 'Proveedores', 'tipo': 'P', 'naturaleza': 'C'},
        {'codigo': '240805', 'nombre': 'IVA por Cobrar', 'tipo': 'P', 'naturaleza': 'C'},
        
        # Ingresos
        {'codigo': '413505', 'nombre': 'Ventas de Mercancía', 'tipo': 'I', 'naturaleza': 'C'},
        
        # Gastos
        {'codigo': '510505', 'nombre': 'Gastos de Nómina', 'tipo': 'G', 'naturaleza': 'D'},
        {'codigo': '613505', 'nombre': 'Costo de Venta', 'tipo': 'G', 'naturaleza': 'D'},
    ]
    
    for cuenta_data in cuentas:
        cuenta, created = CuentaContable.objects.get_or_create(
            codigo=cuenta_data['codigo'],
            defaults=cuenta_data
        )
        if created:
            print(f"✅ Cuenta contable: {cuenta.nombre}")

def crear_almacen_principal():
    """Crear almacén principal"""
    almacen, created = Almacen.objects.get_or_create(
        codigo='PRINCIPAL',
        defaults={
            'nombre': 'Almacén Principal',
            'activo': True
        }
    )
    print(f"✅ Almacén: {almacen.nombre}")
    return almacen

def crear_empleados():
    """Crear empleados de prueba"""
    empleados = [
        {
            'cedula': '001-1234567-8',
            'nombres': 'María',
            'apellidos': 'García López',
            'puesto': 'Gerente General',
            'departamento': 'Gerencia',
            'salario_base': 80000,
            'fecha_ingreso': date(2020, 1, 15)
        },
        {
            'cedula': '002-1234567-8', 
            'nombres': 'Carlos',
            'apellidos': 'Rodríguez Méndez',
            'puesto': 'Contador',
            'departamento': 'Contabilidad',
            'salario_base': 45000,
            'fecha_ingreso': date(2021, 3, 10)
        },
        {
            'cedula': '003-1234567-8',
            'nombres': 'Ana',
            'apellidos': 'Martínez Sánchez',
            'puesto': 'Asistente de Inventario',
            'departamento': 'Inventario', 
            'salario_base': 30000,
            'fecha_ingreso': date(2022, 6, 20)
        }
    ]
    
    for emp_data in empleados:
        empleado, created = Empleado.objects.get_or_create(
            cedula=emp_data['cedula'],
            defaults=emp_data
        )
        if created:
            print(f"✅ Empleado: {empleado.nombres} {empleado.apellidos}")

def crear_clientes_proveedores():
    """Crear clientes y proveedores de prueba"""
    entidades = [
        # Clientes
        {
            'nombre_comercial': 'Supermercado Nacional',
            'identificacion_fiscal': '131-1234567-8',
            'tipo': 'C',
            'correo_electronico': 'compras@supermercadonacional.com',
            'plazo_credito_dias': 30
        },
        {
            'nombre_comercial': 'Tiendas La Económica',
            'identificacion_fiscal': '131-8765432-1', 
            'tipo': 'C',
            'correo_electronico': 'contacto@laeconomica.com',
            'plazo_credito_dias': 15
        },
        
        # Proveedores
        {
            'nombre_comercial': 'Distribuidora de Alimentos S.A.',
            'identificacion_fiscal': '101-1122334-5',
            'tipo': 'P',
            'correo_electronico': 'ventas@distribuidora-alimentos.com',
            'plazo_credito_dias': 0
        },
        {
            'nombre_comercial': 'Importadora de Productos S.A.',
            'identificacion_fiscal': '101-5566778-9',
            'tipo': 'P', 
            'correo_electronico': 'pedidos@importadorasa.com',
            'plazo_credito_dias': 0
        }
    ]
    
    for ent_data in entidades:
        entidad, created = EntidadComercial.objects.get_or_create(
            identificacion_fiscal=ent_data['identificacion_fiscal'],
            defaults=ent_data
        )
        tipo = "Cliente" if ent_data['tipo'] == 'C' else "Proveedor"
        if created:
            print(f"✅ {tipo}: {entidad.nombre_comercial}")

def crear_productos_adicionales():
    """Crear productos adicionales de prueba"""
    productos = [
        {
            'nombre': 'Arroz Premium 5kg',
            'codigo_sku': 'ARROZ-PREM-5KG',
            'precio_venta': 250,
            'costo_unitario': 180,
            'unidad_medida': 'Bolsa'
        },
        {
            'nombre': 'Aceite Vegetal 1L',
            'codigo_sku': 'ACEITE-VEG-1L', 
            'precio_venta': 120,
            'costo_unitario': 85,
            'unidad_medida': 'Botella'
        },
        {
            'nombre': 'Leche en Polvo 400g',
            'codigo_sku': 'LECHE-POLVO-400G',
            'precio_venta': 95,
            'costo_unitario': 65, 
            'unidad_medida': 'Bolsa'
        },
        {
            'nombre': 'Servicio de Consultoría ERP',
            'codigo_sku': 'SERV-CONSUL-ERP',
            'tipo': 'S',
            'precio_venta': 5000,
            'costo_unitario': 0,
            'unidad_medida': 'Hora'
        }
    ]
    
    for prod_data in productos:
        producto, created = Producto.objects.get_or_create(
            codigo_sku=prod_data['codigo_sku'],
            defaults=prod_data
        )
        if created:
            print(f"✅ Producto: {producto.nombre}")

def main():
    """Función principal para crear todos los datos de prueba"""
    print("🚀 Creando datos de prueba para ERP Hermes...")
    
    # Crear datos básicos
    moneda = crear_moneda_principal()
    crear_cuentas_contables()
    almacen = crear_almacen_principal()
    
    # Crear datos de negocio
    crear_empleados()
    crear_clientes_proveedores() 
    crear_productos_adicionales()
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("📊 Ahora puedes ver datos reales en los reportes del dashboard")

if __name__ == '__main__':
    main()