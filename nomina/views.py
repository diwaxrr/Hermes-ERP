# Archivo: nomina/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Empleado, ConceptoNomina, PeriodoNomina, NominaEncabezado
from .serializers import (
    EmpleadoSerializer, ConceptoNominaSerializer, 
    PeriodoNominaSerializer, NominaEncabezadoSerializer
)
from central.permissions import IsContabilidadUser

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [IsContabilidadUser]  # Contabilidad gestiona empleados
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar un empleado"""
        empleado = self.get_object()
        empleado.activo = False
        empleado.save()
        return Response({'status': 'Empleado desactivado'})

class ConceptoNominaViewSet(viewsets.ModelViewSet):
    queryset = ConceptoNomina.objects.all()
    serializer_class = ConceptoNominaSerializer
    permission_classes = [IsContabilidadUser]

class PeriodoNominaViewSet(viewsets.ModelViewSet):
    queryset = PeriodoNomina.objects.all()
    serializer_class = PeriodoNominaSerializer
    permission_classes = [IsContabilidadUser]
    
    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        """Cerrar un período de nómina"""
        periodo = self.get_object()
        if periodo.estado == 'A':  # Solo se pueden cerrar períodos abiertos
            periodo.estado = 'C'
            periodo.save()
            return Response({'status': 'Período cerrado'})
        return Response(
            {'error': 'Solo se pueden cerrar períodos abiertos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class NominaEncabezadoViewSet(viewsets.ModelViewSet):
    queryset = NominaEncabezado.objects.all()
    serializer_class = NominaEncabezadoSerializer
    permission_classes = [IsContabilidadUser]
    
    @action(detail=True, methods=['post'])
    def calcular_automatico(self, request, pk=None):
        """Calcular nómina automáticamente basado en conceptos fijos"""
        nomina = self.get_object()
        empleado = nomina.empleado
        
        # Aquí iría la lógica de cálculo automático
        # Por ahora solo un mensaje de placeholder
        return Response({
            'status': 'Cálculo automático en desarrollo',
            'empleado': empleado.nombres,
            'salario_base': empleado.salario_base
        })