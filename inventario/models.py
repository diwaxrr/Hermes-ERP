# Archivo: inventario/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
# Importamos modelos del Núcleo
from central.models import Producto 

# ----------------------------------------------------------------------
# 1. ALMACÉN (Ubicación física del stock)
# ----------------------------------------------------------------------

class Almacen(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Nombre del Almacén"),
        help_text=_("Ej. Almacén Principal, Tienda 1, Bodega de Devoluciones.")
    )
    codigo = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_("Código de Almacén")
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Almacén")
        verbose_name_plural = _("Almacenes")


# ----------------------------------------------------------------------
# 2. STOCK (Cantidad actual por Producto y Almacén)
# ----------------------------------------------------------------------

class Stock(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name=_("Producto")
    )
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        verbose_name=_("Almacén")
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Cantidad en Stock")
    )

    def __str__(self):
        return f"{self.producto.nombre} en {self.almacen.nombre}: {self.cantidad}"

    class Meta:
        verbose_name = _("Stock")
        verbose_name_plural = _("Existencias de Stock")
        unique_together = ('producto', 'almacen')
        ordering = ['producto__nombre']


# ----------------------------------------------------------------------
# 3. MOVIMIENTO DE INVENTARIO (Registro de entradas y salidas)
# ----------------------------------------------------------------------

TIPO_MOVIMIENTO_CHOICES = [
    ('E', 'Entrada (Compra/Ajuste Positivo)'),
    ('S', 'Salida (Venta/Ajuste Negativo)'),
]

class MovimientoInventario(models.Model):
    fecha = models.DateField(auto_now_add=True)
    tipo_movimiento = models.CharField(
        max_length=1,
        choices=TIPO_MOVIMIENTO_CHOICES,
        verbose_name=_("Tipo de Movimiento")
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name=_("Producto")
    )
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        verbose_name=_("Almacén de Origen/Destino")
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Cantidad Movida")
    )
    referencia_doc = models.CharField(
        max_length=100,
        verbose_name=_("Referencia de Documento"),
        help_text=_("Ej. Número de Factura, Orden de Compra.")
    )
    # Enlace crítico al Núcleo: Registra el asiento contable generado
    asiento_contable_nucleo = models.ForeignKey(
        'central.TransaccionEncabezado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Asiento Contable Relacionado")
    )
    
    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} {self.producto.nombre} - {self.cantidad} ({self.fecha})"

    class Meta:
        verbose_name = _("Movimiento de Inventario")
        verbose_name_plural = _("Movimientos de Inventario")
        ordering = ['-fecha']