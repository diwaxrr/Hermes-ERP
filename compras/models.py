# Archivo: compras/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from central.models import Producto, EntidadComercial, Moneda

# ==============================================================================
# MODELOS DE COMPRAS
# ==============================================================================

class OrdenCompra(models.Model):
    """Orden de compra a proveedores"""
    
    ESTADO_ORDEN = [
        ('B', 'Borrador'),
        ('E', 'Emitida'),
        ('R', 'Recibida Parcialmente'),
        ('C', 'Completada'),
        ('A', 'Anulada'),
    ]
    
    # Identificación
    numero_orden = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Número de Orden"),
        help_text=_("Número consecutivo único de orden de compra.")
    )
    fecha_emision = models.DateField(
        verbose_name=_("Fecha de Emisión")
    )
    fecha_esperada = models.DateField(
        verbose_name=_("Fecha Esperada de Entrega")
    )
    
    # Relaciones
    proveedor = models.ForeignKey(
        EntidadComercial,
        on_delete=models.PROTECT,
        limit_choices_to={'tipo__in': ['P', 'A']},  # Solo proveedores
        verbose_name=_("Proveedor")
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
    
    # Estado
    estado = models.CharField(
        max_length=1,
        choices=ESTADO_ORDEN,
        default='B',
        verbose_name=_("Estado")
    )
    
    def __str__(self):
        return f"OC {self.numero_orden} - {self.proveedor.nombre_comercial}"
    
    class Meta:
        verbose_name = _("Orden de Compra")
        verbose_name_plural = _("Órdenes de Compra")
        ordering = ['-fecha_emision', 'numero_orden']


class OrdenCompraDetalle(models.Model):
    """Líneas de detalle de una orden de compra"""
    
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name=_("Orden de Compra")
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name=_("Producto")
    )
    cantidad_solicitada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Cantidad Solicitada")
    )
    cantidad_recibida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Cantidad Recibida")
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
        return f"{self.producto.nombre} x {self.cantidad_solicitada}"
    
    class Meta:
        verbose_name = _("Detalle de Orden de Compra")
        verbose_name_plural = _("Detalles de Orden de Compra")


class RecepcionCompra(models.Model):
    """Recepción de mercancía contra orden de compra"""
    
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.PROTECT,
        related_name='recepciones',
        verbose_name=_("Orden de Compra")
    )
    fecha_recepcion = models.DateField(
        verbose_name=_("Fecha de Recepción")
    )
    referencia = models.CharField(
        max_length=50,
        verbose_name=_("Referencia/Número de Recepción")
    )
    
    # Enlace con inventario
    movimiento_inventario = models.ForeignKey(
        'inventario.MovimientoInventario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Movimiento de Inventario Relacionado")
    )
    
    def __str__(self):
        return f"Recepción {self.referencia} - {self.orden_compra.numero_orden}"
    
    class Meta:
        verbose_name = _("Recepción de Compra")
        verbose_name_plural = _("Recepciones de Compra")
        ordering = ['-fecha_recepcion']