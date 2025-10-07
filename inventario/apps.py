# Archivo: inventario/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'
    verbose_name = _("Módulo de Inventario")

    def ready(self):
        # Importa el archivo de señales cuando la aplicación esté lista
        import inventario.signals