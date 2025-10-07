# Archivo: inventario/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import MovimientoInventario, Stock

@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock_post_movimiento(sender, instance, created, **kwargs):
    """
    Se ejecuta después de que un MovimientoInventario es creado (guardado).
    Actualiza la tabla Stock sumando o restando la cantidad movida.
    """
    # Solo actuar cuando se crea un nuevo movimiento
    if created:
        producto = instance.producto
        almacen = instance.almacen
        cantidad_movida = instance.cantidad
        tipo = instance.tipo_movimiento

        with transaction.atomic():
            # Obtener o crear la entrada de Stock
            stock, created = Stock.objects.get_or_create(
                producto=producto, 
                almacen=almacen,
                defaults={'cantidad': 0} 
            )

            # Aplicar el movimiento
            if tipo == 'E':  # Entrada (Suma stock)
                stock.cantidad += cantidad_movida
            elif tipo == 'S':  # Salida (Resta stock)
                stock.cantidad -= cantidad_movida
            
            stock.save()