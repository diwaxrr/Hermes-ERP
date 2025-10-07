# Archivo: facturacion/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'facturacion'
    verbose_name = _("Módulo de Facturación")