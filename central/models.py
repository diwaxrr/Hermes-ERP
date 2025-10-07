from django.db import models
from django.utils.translation import gettext_lazy as _

# ==============================================================================
# 1. PRODUCTOS Y SERVICIOS
# ==============================================================================

# Opciones para el campo 'tipo' (Tipo de Producto/Servicio)
TIPO_OPCIONES = [
    ('P', 'Producto Físico'),
    ('S', 'Servicio'),
]

# Comentario: Modelo Maestro para la gestión de Productos y Servicios de la empresa.
class Producto(models.Model):
    # Campos de Identificación Básica
    nombre = models.CharField(
        max_length=200,
        verbose_name=_("Nombre del Producto/Servicio"),
        help_text=_("Nombre comercial bajo el cual se vende este ítem.")
    )
    codigo_sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Código SKU"),
        help_text=_("Identificador único para inventario y búsqueda rápida. Ej. SKU-001.")
    )

    # Campo de Clasificación
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_OPCIONES,
        default='P',
        verbose_name=_("Tipo"),
        help_text=_("Define si es un 'P' Producto Físico o un 'S' Servicio.")
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_("Descripción detallada para uso interno y documentos como cotizaciones.")
    )

    # Campos de Precios y Costos
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Precio de Venta"),
        help_text=_("Precio estándar sin incluir impuestos.")
    )
    costo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Costo Unitario"),
        help_text=_("Costo de adquisición o fabricación. Opcional.")
    )

    # Campo de Impuestos
    aplica_impuesto = models.BooleanField(
        default=True,
        verbose_name=_("Aplica Impuesto"),
        help_text=_("Marcar si este producto está sujeto a IVA u otro impuesto de venta.")
    )

    # Campo de Inventario
    unidad_medida = models.CharField(
        max_length=10,
        verbose_name=_("Unidad de Medida"),
        help_text=_("Ej. Unidad, Caja, Litros. Necesario para control de inventario.")
    )

    # Campo de Estado
    activo = models.BooleanField(
        default=True,
        verbose_name=_("Activo"),
        help_text=_("Indica si el producto está disponible para la venta.")
    )

    # Funcionalidad y Métodos
    def __str__(self):
        return f"{self.nombre} ({self.codigo_sku})"

    class Meta:
        verbose_name = _("Producto o Servicio")
        verbose_name_plural = _("Productos y Servicios")
        ordering = ['nombre']


# ==============================================================================
# 2. ENTIDADES COMERCIALES (CLIENTES/PROVEEDORES)
# ==============================================================================

# Opciones para el campo 'tipo' de EntidadComercial
TIPO_ENTIDAD_OPCIONES = [
    ('C', 'Cliente'),
    ('P', 'Proveedor'),
    ('A', 'Ambos'),
]

# Comentario: Modelo Maestro para gestionar Clientes, Proveedores o Ambos.
class EntidadComercial(models.Model):
    # Campos de Identificación Básica
    nombre_comercial = models.CharField(
        max_length=255,
        verbose_name=_("Nombre Comercial"),
        help_text=_("Nombre legal o comercial de la entidad.")
    )
    identificacion_fiscal = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Identificación Fiscal (NIT/RUT)"),
        help_text=_("Número de identificación tributaria (NIT, RUT, Cédula). Debe ser único.")
    )

    # Clasificación
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_ENTIDAD_OPCIONES,
        default='C',
        verbose_name=_("Tipo de Entidad"),
        help_text=_("Clasifica si la entidad es Cliente (C), Proveedor (P) o Ambos (A).")
    )

    # Contacto
    correo_electronico = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Correo Electrónico"),
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("Teléfono de Contacto"),
    )
    direccion_principal = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Dirección Principal"),
    )

    # Condiciones Comerciales
    plazo_credito_dias = models.IntegerField(
        default=0,
        verbose_name=_("Plazo de Crédito (días)"),
        help_text=_("Número de días para el pago a crédito (0 = Contado).")
    )

    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name=_("Activo"),
        help_text=_("Indica si la entidad está activa para transacciones.")
    )

    def __str__(self):
        return f"{self.nombre_comercial} ({self.identificacion_fiscal})"

    class Meta:
        verbose_name = _("Entidad Comercial")
        verbose_name_plural = _("Entidades Comerciales")
        ordering = ['nombre_comercial']


# ==============================================================================
# 3. GESTIÓN MONETARIA Y CONTABLE
# ==============================================================================

# --- MODELO MONEDA ---

# Comentario: Modelo Maestro para gestionar las monedas utilizadas por la empresa.
class Moneda(models.Model):
    codigo_iso = models.CharField(
        max_length=3,
        unique=True,
        verbose_name=_("Código ISO"),
        help_text=_("Código ISO 4217 de la moneda (ej. USD, COP).")
    )
    nombre = models.CharField(
        max_length=50,
        verbose_name=_("Nombre de la Moneda"),
    )
    simbolo = models.CharField(
        max_length=5,
        verbose_name=_("Símbolo"),
    )
    es_principal = models.BooleanField(
        default=False,
        verbose_name=_("Moneda Principal"),
        help_text=_("Marcar solo la moneda base para la contabilidad.")
    )

    def __str__(self):
        return f"{self.codigo_iso} - {self.nombre}"

    class Meta:
        verbose_name = _("Moneda")
        verbose_name_plural = _("Monedas")
        ordering = ['codigo_iso']


# --- MODELO CUENTA CONTABLE ---

TIPO_CUENTA_OPCIONES = [
    ('A', 'Activo'),
    ('P', 'Pasivo'),
    ('R', 'Patrimonio'),
    ('I', 'Ingreso'),
    ('G', 'Gasto'),
]

NATURALEZA_OPCIONES = [
    ('D', 'Débito'),
    ('C', 'Crédito'),
]

# Comentario: Modelo Maestro que establece el Plan de Cuentas Contable.
class CuentaContable(models.Model):
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Código Contable"),
        help_text=_("Código jerárquico de la cuenta contable (ej. 110505).")
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name=_("Nombre de la Cuenta"),
    )
    
    # Clasificación Contable
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_CUENTA_OPCIONES,
        verbose_name=_("Tipo de Cuenta"),
        help_text=_("Activo, Pasivo, Patrimonio, Ingreso o Gasto.")
    )
    naturaleza = models.CharField(
        max_length=1,
        choices=NATURALEZA_OPCIONES,
        verbose_name=_("Naturaleza"),
        help_text=_("Define si la cuenta aumenta con un movimiento Débito o Crédito.")
    )

    # Jerarquía (Relación a sí mismo)
    cuenta_padre = models.ForeignKey(
        'self', # <-- CORREGIDO: Usando cadena para auto-referencia
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='cuentas_hijas',
        verbose_name=_("Cuenta Padre"),
        help_text=_("Enlace a la cuenta inmediatamente superior en la jerarquía contable.")
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name=_("Activo"),
    )

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = _("Cuenta Contable")
        verbose_name_plural = _("Cuentas Contables")
        ordering = ['codigo']


# ==============================================================================
# 4. MOTOR TRANSACCIONAL (ASIENTOS)
# ==============================================================================

# --- MODELO TRANSACCION ENCABEZADO (ASIENTO CONTABLE) ---

# Comentario: Modelo que registra la cabecera de un asiento contable.
class TransaccionEncabezado(models.Model):
    fecha = models.DateField(
        verbose_name=_("Fecha de Transacción"),
        help_text=_("Día en que ocurre la transacción contable.")
    )
    referencia = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Referencia/Documento"),
        help_text=_("Número único de documento (ej. Factura, Recibo de Caja).")
    )
    descripcion = models.TextField(
        verbose_name=_("Descripción"),
        help_text=_("Detalle del propósito de esta transacción.")
    )

    # Relaciones con Maestros
    entidad = models.ForeignKey(
        'EntidadComercial', # <-- CORREGIDO: Usando cadena
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Entidad Comercial"),
        help_text=_("Cliente o Proveedor asociado, si aplica.")
    )
    moneda = models.ForeignKey(
        'Moneda', # <-- CORREGIDO: Usando cadena
        on_delete=models.PROTECT,
        verbose_name=_("Moneda"),
    )
    tasa_cambio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1.0000,
        verbose_name=_("Tasa de Cambio"),
        help_text=_("Tasa utilizada para convertir a la Moneda Principal si es diferente.")
    )

    def __str__(self):
        return f"{self.referencia} - {self.fecha.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = _("Asiento Contable")
        verbose_name_plural = _("Asientos Contables")
        ordering = ['-fecha', 'referencia']


# --- MODELO MOVIMIENTO CONTABLE (DETALLE) ---

TIPO_MOVIMIENTO_OPCIONES = [
    ('D', 'Débito'),
    ('C', 'Crédito'),
]

# Comentario: Registra el detalle de cada línea de un asiento contable.
class MovimientoContable(models.Model):
    encabezado = models.ForeignKey(
        'TransaccionEncabezado', # <-- CORREGIDO: Usando cadena
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name=_("Encabezado de Transacción"),
    )
    cuenta = models.ForeignKey(
        'CuentaContable', # <-- CORREGIDO: Usando cadena
        on_delete=models.PROTECT,
        verbose_name=_("Cuenta Contable"),
    )
    tipo_movimiento = models.CharField(
        max_length=1,
        choices=TIPO_MOVIMIENTO_OPCIONES,
        verbose_name=_("Tipo de Movimiento"),
        help_text=_("Indica si el movimiento es un Débito o un Crédito.")
    )
    monto = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("Monto"),
        help_text=_("Valor del movimiento en la moneda de la transacción.")
    )

    def __str__(self):
        return f"{self.encabezado.referencia} | {self.cuenta.codigo} {self.tipo_movimiento}: {self.monto}"

    class Meta:
        verbose_name = _("Movimiento Contable")
        verbose_name_plural = _("Movimientos Contables")
        ordering = ['encabezado', 'tipo_movimiento']