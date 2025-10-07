# Archivo: central/permissions.py

from rest_framework import permissions

# Permiso 1: Para el Personal de Contabilidad
class IsContabilidadUser(permissions.BasePermission):
    """
    Permite el acceso solo si el usuario pertenece al grupo 'Contabilidad'.
    """
    def has_permission(self, request, view):
        # El grupo 'Contabilidad' es el único que debe poder crear/modificar transacciones.
        return request.user.groups.filter(name='Contabilidad').exists()

# Permiso 2: Para el Personal de Inventario/Operaciones
class IsInventarioUser(permissions.BasePermission):
    """
    Permite el acceso solo si el usuario pertenece al grupo 'Inventario' o 'Contabilidad'.
    Contabilidad a menudo necesita acceso a los maestros (productos).
    """
    def has_permission(self, request, view):
        # Permite acceso al grupo Inventario O al grupo Contabilidad
        return request.user.groups.filter(name__in=['Inventario']).exists()

# Permiso 3: Solo Lectura para los Maestros (para usuarios no administrativos)
class ReadOnly(permissions.BasePermission):
    """
    Permite solo peticiones seguras (GET, HEAD, OPTIONS) a cualquier usuario autenticado.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS