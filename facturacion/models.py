# Archivo: facturacion/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from central.models import Producto, EntidadComercial, Moneda

# ==============================================================================
# MODELOS DE FACTURACIÓN
# ==============================================================================

class FacturaEncabezado(models.Model):
    """Encabezado de factura (documento de venta)"""
    
    ESTADO_FACTURA = [
        ('B', 'Borrador'),
        ('E', 'Emitida'),
        ('A', 'Anulada'),
        ('P', 'Pagada'),
    ]
    
    # Identificación
    numero_factura = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Número de Factura"),
        help_text=_("Número consecutivo único de facturación.")
    )
    fecha_emision = models.DateField(
        verbose_name=_("Fecha de Emisión")
    )
    fecha_vencimiento = models.DateField(
        verbose_name=_("Fecha de Vencimiento")
    )
    
    # Relaciones con maestros
    cliente = models.ForeignKey(
        EntidadComercial,
        on_delete=models.PROTECT,
        limit_choices_to={'tipo__in': ['C', 'A']},  # Solo clientes
        verbose_name=_("Cliente")
    )
    moneda = models.ForeignKey(
        Moneda,
        on_delete=models.PROTECT,
        verbose_name=_("Moneda")
    )
    
    # Campos financieros
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Subtotal")
    )
    impuesto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Impuesto")
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Total")
    )
    
    # Estado y control
    estado = models.CharField(
        max_length=1,
        choices=ESTADO_FACTURA,
        default='B',
        verbose_name=_("Estado")
    )
    
    # Enlace con contabilidad
    asiento_contable = models.ForeignKey(
        'central.TransaccionEncabezado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Asiento Contable Relacionado")
    )
    
    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente.nombre_comercial}"
    
    class Meta:
        verbose_name = _("Factura")
        verbose_name_plural = _("Facturas")
        ordering = ['-fecha_emision', 'numero_factura']


class FacturaDetalle(models.Model):
    """Líneas de detalle de una factura"""
    
    factura = models.ForeignKey(
        FacturaEncabezado,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name=_("Factura")
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name=_("Producto/Servicio")
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Cantidad")
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Precio Unitario")
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Subtotal Línea")
    )
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
    
    class Meta:
        verbose_name = _("Detalle de Factura")
        verbose_name_plural = _("Detalles de Factura")


class Pago(models.Model):
    """Registro de pagos recibidos"""
    
    METODO_PAGO = [
        ('EF', 'Efectivo'),
        ('TB', 'Transferencia Bancaria'),
        ('TC', 'Tarjeta de Crédito'),
        ('TD', 'Tarjeta de Débito'),
    ]
    
    factura = models.ForeignKey(
        FacturaEncabezado,
        on_delete=models.PROTECT,
        related_name='pagos',
        verbose_name=_("Factura")
    )
    fecha_pago = models.DateField(
        verbose_name=_("Fecha de Pago")
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Monto Pagado")
    )
    metodo_pago = models.CharField(
        max_length=2,
        choices=METODO_PAGO,
        verbose_name=_("Método de Pago")
    )
    referencia = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Referencia/Número de Transacción")
    )
    
    # Enlace con contabilidad
    asiento_contable = models.ForeignKey(
        'central.TransaccionEncabezado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Asiento Contable del Pago")
    )
    
    def __str__(self):
        return f"Pago {self.referencia} - {self.monto}"
    
    class Meta:
        verbose_name = _("Pago")
        verbose_name_plural = _("Pagos")
        ordering = ['-fecha_pago']