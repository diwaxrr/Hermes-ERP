# Archivo: nomina/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

# ==============================================================================
# MODELOS DE NÓMINA
# ==============================================================================

class Empleado(models.Model):
    """Información básica de empleados"""
    
    TIPO_CONTRATO = [
        ('F', 'Tiempo Fijo'),
        ('I', 'Indefinido'),
        ('O', 'Por Obra/Labor'),
    ]
    
    # Relación con usuario del sistema (opcional)
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Usuario del Sistema")
    )
    
    # Información personal
    cedula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Cédula/Pasaporte")
    )
    nombres = models.CharField(
        max_length=100,
        verbose_name=_("Nombres")
    )
    apellidos = models.CharField(
        max_length=100,
        verbose_name=_("Apellidos")
    )
    fecha_ingreso = models.DateField(
        verbose_name=_("Fecha de Ingreso")
    )
    
    # Información laboral
    puesto = models.CharField(
        max_length=100,
        verbose_name=_("Puesto de Trabajo")
    )
    departamento = models.CharField(
        max_length=100,
        verbose_name=_("Departamento")
    )
    tipo_contrato = models.CharField(
        max_length=1,
        choices=TIPO_CONTRATO,
        verbose_name=_("Tipo de Contrato")
    )
    salario_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Salario Base Mensual")
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name=_("Activo")
    )
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.puesto}"
    
    class Meta:
        verbose_name = _("Empleado")
        verbose_name_plural = _("Empleados")
        ordering = ['apellidos', 'nombres']


class ConceptoNomina(models.Model):
    """Conceptos de nómina (devengos y deducciones)"""
    
    TIPO_CONCEPTO = [
        ('D', 'Devengo (Ingreso)'),
        ('C', 'Deducción (Descuento)'),
    ]
    
    NATURALEZA = [
        ('F', 'Fijo'),
        ('V', 'Variable'),
    ]
    
    codigo = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_("Código del Concepto")
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name=_("Nombre del Concepto")
    )
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_CONCEPTO,
        verbose_name=_("Tipo de Concepto")
    )
    naturaleza = models.CharField(
        max_length=1,
        choices=NATURALEZA,
        verbose_name=_("Naturaleza")
    )
    valor_fijo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Valor Fijo")
    )
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Porcentaje")
    )
    base_calculo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Base de Cálculo"),
        help_text=_("Ej: SALARIO_BASE, TOTAL_DEVENGOS")
    )
    
    # Enlace contable
    cuenta_contable = models.ForeignKey(
        'central.CuentaContable',
        on_delete=models.PROTECT,
        verbose_name=_("Cuenta Contable")
    )
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta:
        verbose_name = _("Concepto de Nómina")
        verbose_name_plural = _("Conceptos de Nómina")


class PeriodoNomina(models.Model):
    """Períodos de nómina (quincenas, meses)"""
    
    ESTADO_PERIODO = [
        ('A', 'Abierto'),
        ('C', 'Cerrado'),
        ('P', 'Procesado'),
    ]
    
    descripcion = models.CharField(
        max_length=100,
        verbose_name=_("Descripción del Período")
    )
    fecha_inicio = models.DateField(
        verbose_name=_("Fecha de Inicio")
    )
    fecha_fin = models.DateField(
        verbose_name=_("Fecha de Fin")
    )
    fecha_pago = models.DateField(
        verbose_name=_("Fecha de Pago")
    )
    estado = models.CharField(
        max_length=1,
        choices=ESTADO_PERIODO,
        default='A',
        verbose_name=_("Estado")
    )
    
    def __str__(self):
        return f"{self.descripcion} ({self.fecha_inicio} - {self.fecha_fin})"
    
    class Meta:
        verbose_name = _("Período de Nómina")
        verbose_name_plural = _("Períodos de Nómina")
        ordering = ['-fecha_inicio']


class NominaEncabezado(models.Model):
    """Encabezado de nómina por empleado y período"""
    
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        verbose_name=_("Empleado")
    )
    periodo = models.ForeignKey(
        PeriodoNomina,
        on_delete=models.PROTECT,
        verbose_name=_("Período de Nómina")
    )
    
    # Totales
    total_devengos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Total Devengos")
    )
    total_deducciones = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Total Deducciones")
    )
    neto_a_pagar = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Neto a Pagar")
    )
    
    # Enlace contable
    asiento_contable = models.ForeignKey(
        'central.TransaccionEncabezado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Asiento Contable")
    )
    
    def __str__(self):
        return f"Nómina {self.empleado} - {self.periodo}"
    
    class Meta:
        verbose_name = _("Nómina")
        verbose_name_plural = _("Nóminas")
        unique_together = ['empleado', 'periodo']


class NominaDetalle(models.Model):
    """Detalle de conceptos por nómina"""
    
    nomina = models.ForeignKey(
        NominaEncabezado,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name=_("Nómina")
    )
    concepto = models.ForeignKey(
        ConceptoNomina,
        on_delete=models.PROTECT,
        verbose_name=_("Concepto")
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        verbose_name=_("Cantidad")
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Valor")
    )
    
    def __str__(self):
        return f"{self.concepto.nombre}: {self.valor}"
    
    class Meta:
        verbose_name = _("Detalle de Nómina")
        verbose_name_plural = _("Detalles de Nómina")