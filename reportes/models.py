from django.db import models
from django.utils.translation import gettext_lazy as _

class ReporteConfiguracion(models.Model):
    TIPO_REPORTE_CHOICES = [
        ('INV', 'Inventario'),
        ('VEN', 'Ventas'),
        ('COM', 'Compras'),
        ('NOM', 'Nómina'),
        ('CON', 'Contabilidad'),
    ]

    nombre = models.CharField(
        max_length=100,
        verbose_name=_("Nombre del Reporte"),
        help_text=_("Nombre descriptivo del reporte")
    )
    tipo_reporte = models.CharField(
        max_length=3,
        choices=TIPO_REPORTE_CHOICES,
        verbose_name=_("Tipo de Reporte")
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Código del Reporte")
    )
    activo = models.BooleanField(default=True)
    configuracion_json = models.JSONField(
        default=dict,
        verbose_name=_("Configuración JSON"),
        help_text=_("Parámetros y configuración específica del reporte")
    )

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = _("Configuración de Reporte")
        verbose_name_plural = _("Configuraciones de Reportes")