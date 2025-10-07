# Archivo: reportes/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportes'
    verbose_name = _("Módulo de Reportes")