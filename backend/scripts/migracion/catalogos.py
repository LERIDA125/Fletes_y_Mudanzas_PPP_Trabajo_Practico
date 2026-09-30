"""Catálogos de normalización de la migración de datos históricos.

**Todos los catálogos de este módulo son PROVISIONALES.** No están definidos en ninguna spec ni
en AGENTS.md: se armaron a partir de los valores que aparecen en el archivo de Excel para poder
cargar algo, y cada uno queda anotado como decisión pendiente de confirmar con el cliente
(AGENTS.md §6). El script no elige entre dos valores: cuando no puede decidir con confianza, manda
el caso a `revision.RevisionHumana` en vez de forzar una categoría.

Este módulo es parte de la transformación (capa de Infraestructura): contiene tablas de búsqueda
de texto, no reglas de negocio.
"""

from __future__ import annotations

from typing import Final

# ================================================================================================
# Tipo de vehículo
# ================================================================================================

#: Catálogo canónico de tipos de vehículo. Provisional: la forma exacta del catálogo (y si
#: `Camioneta` a secas es una categoría o debería tener tamaño) no está confirmada por el cliente.
TIPOS_VEHICULO_CANONICOS: Final[tuple[str, ...]] = (
    "Utilitario",
    "Furgón Chico",
    "Furgón Mediano",
    "Furgón Grande",
    "Camioneta",
    "Camioneta Mediana",
    "Camioneta Grande",
    "Camión Mudancero",
)

#: Alias observados en la planilla -> valor canónico. La clave es la forma normalizada
#: (minúsculas, sin acentos, espacios colapsados); la compara `normalizacion.normalizar_texto`.
ALIAS_TIPO_VEHICULO: Final[dict[str, str]] = {
    "utilitario": "Utilitario",
    "furgon chico": "Furgón Chico",
    "furgon mediano": "Furgón Mediano",
    "furgon grande": "Furgón Grande",
    "camioneta": "Camioneta",
    "camioneta mediana": "Camioneta Mediana",
    "camioneta grande": "Camioneta Grande",
    "camion mudancero": "Camión Mudancero",
    # Provisional: la capacidad embebida (3500 kg) es la de un mudancero, pero podría ser un
    # camión de carga general. Requiere confirmación.
    "camion 3500kg": "Camión Mudancero",
}

# ================================================================================================
# Estado del móvil / chofer
# ================================================================================================

#: Estados canónicos pedidos para la migración.
ESTADO_DISPONIBLE: Final = "disponible"
ESTADO_OCUPADO: Final = "ocupado"
ESTADO_INACTIVO: Final = "inactivo"

ESTADOS_CANONICOS: Final[tuple[str, ...]] = (
    ESTADO_DISPONIBLE,
    ESTADO_OCUPADO,
    ESTADO_INACTIVO,
)

#: Texto de la planilla -> estado canónico. Un texto que no está acá NO se fuerza: se marca para
#: revisión humana. Los valores de acá marcados como dudosos también se marcan igual.
ALIAS_ESTADO_MOVIL: Final[dict[str, str]] = {
    "disponible": ESTADO_DISPONIBLE,
    "libre": ESTADO_DISPONIBLE,
    "en viaje": ESTADO_OCUPADO,
    "suspendido por choque": ESTADO_INACTIVO,
    "rompio el elastico": ESTADO_INACTIVO,
}

#: Textos que se mapean a un estado provisional pero que se reportan igual para que alguien los
#: confirme: se puede leer de dos maneras y la elección cambia si al chofer se lo puede agendar.
ESTADOS_AMBIGUOS: Final[dict[str, str]] = {
    # El chofer está disponible pero el móvil está en el taller: no se puede agendar. Se mapea a
    # `inactivo` (la lectura más restrictiva) hasta que se confirme qué significa el estado.
    "en taller hasta el martes": ESTADO_INACTIVO,
    # "De franco" es una ausencia, no una baja: el chofer sigue en el padrón y vuelve. Se mapea a
    # `disponible` (la lectura más permisiva). Si el cliente lo considera `inactivo`, cambia.
    "de franco": ESTADO_DISPONIBLE,
}

# ================================================================================================
# Condición de IVA
# ================================================================================================

CONDICIONES_IVA_CANONICAS: Final[tuple[str, ...]] = (
    "Responsable Inscripto",
    "Consumidor Final",
    "Exento",
)

ALIAS_CONDICION_IVA: Final[dict[str, str]] = {
    "responsable inscripto": "Responsable Inscripto",
    "resp. inscripto": "Responsable Inscripto",
    "responsable inscripto (ri)": "Responsable Inscripto",
    "consumidor final": "Consumidor Final",
    "consumidor final (cf)": "Consumidor Final",
    "exento": "Exento",
}

# ================================================================================================
# Medios de pago y estado de cobro
# ================================================================================================

#: NO existe un catálogo de medios de pago en el repo (ni en AGENTS.md, ni en las specs de H1). Se
#: arma acá a partir de lo que dice la columna `Estado_Cobro` de la planilla y queda pendiente de
#: confirmación: la decisión le corresponde a quien modeló pagos (H10), no a la migración.
MEDIO_EFECTIVO: Final = "Efectivo"
MEDIO_TRANSFERENCIA: Final = "Transferencia bancaria"
MEDIO_CHEQUE: Final = "Cheque"

MEDIOS_PAGO_PROPUESTOS: Final[tuple[str, ...]] = (
    MEDIO_EFECTIVO,
    MEDIO_TRANSFERENCIA,
    MEDIO_CHEQUE,
)

#: Estado de cobro canónico del pago.
COBRO_COBRADO: Final = "cobrado"
COBRO_PARCIAL: Final = "parcial"
COBRO_PENDIENTE: Final = "pendiente"

ESTADOS_COBRO_CANONICOS: Final[tuple[str, ...]] = (
    COBRO_COBRADO,
    COBRO_PARCIAL,
    COBRO_PENDIENTE,
)

#: `(palabra clave, medio de pago canónico)`. Se evalúan en orden y gana la primera coincidencia.
PATRONES_MEDIO_PAGO: Final[tuple[tuple[str, str], ...]] = (
    ("efectivo", MEDIO_EFECTIVO),
    ("en mano", MEDIO_EFECTIVO),
    ("al chofer", MEDIO_EFECTIVO),
    ("transf", MEDIO_TRANSFERENCIA),
    ("transferido", MEDIO_TRANSFERENCIA),
    ("transferencia", MEDIO_TRANSFERENCIA),
    ("cheque", MEDIO_CHEQUE),
)

#: Reglas de descomposición de `Estado_Cobro`. La columna mezcla tres conceptos distintos (medio de
#: pago, estado y monto de seña) en un solo texto libre; cada concepto se reconoce por palabras
#: clave y lo que no se reconoce con confianza queda en `None` + revisión humana.
#:
#: El orden importa: se evalúa **parcial antes que cobrado** a propósito, porque `"Pagó mitad resta
#: factura"` dice "pagó" y no es un cobro completo. Por eso la lista de "cobrado" no incluye la raíz
#: `pago`/`pagó` suelta: con esa raíz no se distinguen `"Paga a 30 días"` de `"Pagó la mitad"`, y
#: adivinar el saldo de un cliente no es asunto de esta migración.
PATRONES_ESTADO_PARCIAL: Final[tuple[str, ...]] = (
    "mitad",
    "sena",
    "parte",
    "resta",
    "debe el resto",
    "debo",
)

PATRONES_ESTADO_COBRADO: Final[tuple[str, ...]] = (
    "todo",
    "completo",
    "total",
    "cobrado",
    "pagada",
    "integrado",
)

PATRONES_ESTADO_PENDIENTE: Final[tuple[str, ...]] = (
    "pendiente",
    "diferido",
    "a 15 dias",
    "a 30 dias",
    "a 60 dias",
    "a consultar",
)

#: `Estado_Cobro` completo que NO se puede mapear a ningún medio de pago ni estado con confianza.
#: Cada entrada dice por qué. Si alguno aparece en el reporte, hay que decidirlo con el cliente.
COBROS_AMBIGUOS: Final[dict[str, str]] = {
    "anotado en la libreta": (
        "No dice medio de pago ni si el cobro está completo. 'La libreta' podría ser la libreta de "
        "cuenta corriente del cliente o el cuaderno del chofer: son dos cosas distintas."
    ),
    "cta cte": (
        "Es una condición de pago, no un medio de pago. No se sabe si el cobro se hizo y por qué "
        "medio, ni si se emitió factura."
    ),
    "pago mitad resta factura": (
        "Dice que se pagó la mitad, pero no dice con qué medio ni si la factura por el resto "
        "cuenta como cobrado. El saldo queda sin calcular a propósito."
    ),
    "sena $5000 debe el resto": (
        "El monto de la seña está explícito pero el medio de pago no. El saldo sí se puede "
        "calcular."
    ),
    "sena 50%": (
        "El porcentaje está explícito pero el medio de pago no. El saldo sí se puede calcular."
    ),
    "cheque diferido": (
        "El medio es cheque, pero 'diferido' no aclara si el cheque está en poder del cliente o si "
        "la fecha de cobro vence dentro o fuera del período. No se fuerza el saldo."
    ),
}

# ================================================================================================
# Direcciones
# ================================================================================================

#: Palabras que delatan que el campo NO es una dirección postal sino una instrucción de retiro.
#: El `Cliente` de H1 exige `direccion_habitual` con 5 a 250 caracteres pero no tiene forma de
#: marcar que el texto no es una dirección, así que estos valores se guardan tal cual y además se
#: reportan como gap (ver `reporte.py`).
INDICADORES_DIRECCION_NO_ESTRUCTURADA: Final[tuple[str, ...]] = (
    "retira en",
    "retirar en",
    "a retirar",
    "deposito",
    "depósito",
    "consultar",
    "sin domicilio",
    "domicilio a confirmar",
)

# ================================================================================================
# Unidades de capacidad de carga
# ================================================================================================

#: Factor a kg para cada unidad encontrada en `Capacidad_Carga`. Las toneladas valen 1000 kg.
FACTORES_UNIDAD_CARGA: Final[dict[str, int]] = {
    "kg": 1,
    "kgs": 1,
    "kilo": 1,
    "kilos": 1,
    "tn": 1000,
    "t": 1000,
    "tonelada": 1000,
    "toneladas": 1000,
    "ton": 1000,
    "tons": 1000,
}

#: Sin unidad escrita se asume kg, que es la unidad de todas las celdas con unidad. Se reporta
#: igual.
UNIDAD_CARGA_POR_DEFECTO: Final = "kg"
