"""Funciones puras de normalización de la migración.

Cada función es **pura**: recibe texto sucio de la planilla y devuelve un valor normalizado, sin
tocar la base de datos, sin leer archivos y sin decidir reglas de negocio. Cuando no puede
resolver un dato con confianza devuelve `None` (o un motivo) para que la capa de transformación lo
mande a revisión humana en vez de adivinar (AGENTS.md §6).

No usan `pandas` ni `datetime.now()`: son determinísticas y se testean sin fixtures.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal, InvalidOperation

from app.domain.cliente import (
    TELEFONO_DIGITOS_MAX,
    TELEFONO_DIGITOS_MIN,
    normalizar_razon_social,
)
from scripts.migracion import catalogos as cat

# ================================================================================================
# Texto
# ================================================================================================


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sin acentos y sin espacios sobrantes, para comparar contra los catálogos.

    Reusa la clave de comparación que ya normaliza la razón social en H1, así los dos caminos
    (búsqueda de clientes y catálogo de la migración) devuelven exactamente lo mismo.
    """
    return normalizar_razon_social(texto)


def _colapsar(texto: str) -> str:
    return " ".join(texto.split())


def _quitar_acentos(texto: str) -> str:
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if not unicodedata.combining(caracter)
    )


# ================================================================================================
# Códigos con prefijo inconsistente
# ================================================================================================

RE_CODIGO = re.compile(r"^(?P<prefijo>[A-Za-z]*)\s*-?\s*(?P<numero>\d+)$")

# Ancho con el que se rellenan los ceros de cada código. Sale de lo que se ve en la planilla
# (`MOV-01`, `VJ-2001`, `CLI-101`). Si el cliente cambia la numeración, se ajusta acá.
ANCHO_NUMERO_MOVIL = 2
ANCHO_NUMERO_VIAJE = 4
ANCHO_NUMERO_CLIENTE = 3


@dataclass(frozen=True)
class Codigo:
    """Un código de la planilla ya normalizado a `PREFIJO-0000`."""

    prefijo: str
    numero: int
    ancho: int

    @property
    def valor(self) -> str:
        return f"{self.prefijo}-{str(self.numero).zfill(self.ancho)}"

    def __str__(self) -> str:
        return self.valor


def normalizar_codigo(valor: object, prefijo_esperado: str, ancho: int) -> Codigo | None:
    """Normaliza `"MOV-01"`, `"MOV01"` y `"03"` al mismo `MOV-01`.

    Acepta el número con o sin prefijo, con o sin guion y con ceros de relleno: son la misma
    clave escrita de tres maneras. Devuelve `None` si no hay ningún número reconocible, que en la
    planilla sería un dato y no una variante de formato.
    """
    if valor is None:
        return None
    texto = _colapsar(str(valor).strip())
    if not texto:
        return None
    coincidencia = RE_CODIGO.match(texto)
    if coincidencia is None:
        return None
    prefijo = (coincidencia.group("prefijo") or "").upper() or prefijo_esperado
    return Codigo(
        prefijo=prefijo,
        numero=int(coincidencia.group("numero")),
        ancho=ancho,
    )


def codigo_de_movil(valor: object) -> Codigo | None:
    return normalizar_codigo(valor, "MOV", ANCHO_NUMERO_MOVIL)


def codigo_de_viaje(valor: object) -> Codigo | None:
    return normalizar_codigo(valor, "VJ", ANCHO_NUMERO_VIAJE)


def codigo_de_cliente(valor: object) -> Codigo | None:
    return normalizar_codigo(valor, "CLI", ANCHO_NUMERO_CLIENTE)


# ================================================================================================
# Teléfonos
# ================================================================================================

RE_TODOS_DIGITOS = re.compile(r"\d")

#: Frases con las que alguien anotó "no tengo teléfono" en la columna de contacto. No se inventa un
#: teléfono: se devuelven como `None`.
FRASES_SIN_TELEFONO = (
    "no tiene",
    "no tengo",
    "sin telefono",
    "sin whatsapp",
    "no tiene whatsapp",
    "no tiene telefono",
    "n/a",
    "-",
)


@dataclass(frozen=True)
class Telefono:
    """Teléfono normalizado a solo dígitos, con el conteo para validarlo contra H1."""

    digitos: str
    digitos_con_pais: bool

    @property
    def es_valido_para_h1(self) -> bool:
        return TELEFONO_DIGITOS_MIN <= len(self.digitos) <= TELEFONO_DIGITOS_MAX


def normalizar_telefono(valor: object) -> tuple[Telefono | None, str | None]:
    """De `"+54 9 11 4455-6677"` a `"5491144556677"`.

    No toca el prefijo de país ni el `0` inicial: decides cómo se guardan los teléfonos-nationales
    es una regla del negocio que H1 dejó abierta (DD-4 en AGENTS.md §11) y esta migración no la
    cierra. Solo saca los separadores y marca los prefijos internacionales con un flag.

    Devuelve `(telefono, motivo)` donde `motivo` dice por qué no se pudo normalizar.
    """
    if valor is None:
        return None, "celda vacía"
    texto = _colapsar(str(valor).strip())
    if not texto:
        return None, "celda vacía"
    if normalizar_texto(texto) in FRASES_SIN_TELEFONO:
        return None, f"«{texto}» no es un teléfono, es una anotación"
    digitos = "".join(RE_TODOS_DIGITOS.findall(texto))
    if not digitos:
        return None, f"«{texto}» no tiene ningún dígito"
    tiene_pais = bool(re.match(r"^\+?(54|54\s*9|00)", texto.replace(" ", "")))
    return Telefono(digitos=digitos, digitos_con_pais=tiene_pais), None


# ================================================================================================
# Fechas
# ================================================================================================

MESES_EN_TEXTO: dict[str, int] = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

RE_ISO = re.compile(r"^(?P<anio>\d{4})-(?P<mes>\d{1,2})-(?P<dia>\d{1,2})$")
RE_DMY = re.compile(r"^(?P<dia>\d{1,2})[/\-](?P<mes>\d{1,2})[/\-](?P<anio>\d{2}|\d{4})$")
RE_TEXTO_MES = re.compile(
    r"^(?P<dia>\d{1,2})\s*(?:de\s+)?(?P<mes>[a-zA-ZáéíóúñÁÉÍÓÚÑ]+)\s*(?:de\s+)?(?P<anio>\d{4})$"
)

#: Un año de dos dígitos anterior a este pivote se interpretaría como 19xx. `26` → 2026.
#: Es el mismo criterio que usa `datetime.strptime("%y")`. Se reporta como supuesto porque ningún
#: dato de la planilla lo confirma: si el archivo tuviera viajes de 1965, esto los traería a 2065.
ANIO_PIVOTE = 50


@dataclass(frozen=True)
class FechaNormalizada:
    """Una fecha ya parseada, con los supuestos que hubo que hacer para llegar a ella."""

    valor: date
    formato_origen: str
    anio_supuesto: bool


def _interpretar_anio(anio: int) -> tuple[int, bool]:
    """Un año de 2 dígitos se proyecta al siglo XXI. Devuelve `(anio, fue_supuesto)`."""
    if anio >= 100:
        return anio, False
    proyectado = 2000 + anio if anio < ANIO_PIVOTE else 1900 + anio
    return proyectado, True


def normalizar_fecha(valor: object) -> tuple[FechaNormalizada | None, str | None]:
    """Parsea los cuatro formatos de `Fecha_Servicio` a una `date`.

    Acepta `dd/mm/aaaa`, `aaaa-mm-dd`, `"16 de Mayo 2026"` y `dd/mm/aa`. **No assumes el formato por
    la posición de la columna**: se prueban todos contra cada celda y el que encaja es el que se
    usa, así que si mañana la planilla mezcla los formatos en otra columna sigue funcionando.

    Devuelve `(fecha, motivo)` donde `motivo` no es `None` si no se pudo parsear.
    """
    if valor is None:
        return None, "celda vacía"
    if isinstance(valor, date):
        return (
            FechaNormalizada(
                valor=valor,
                formato_origen="celda Excel como fecha",
                anio_supuesto=False,
            ),
            None,
        )

    texto = _colapsar(str(valor).strip())
    if not texto:
        return None, "celda vacía"

    coincidencia = RE_ISO.match(texto)
    if coincidencia:
        fecha = _armar_fecha(
            int(coincidencia.group("anio")),
            int(coincidencia.group("mes")),
            int(coincidencia.group("dia")),
        )
        if fecha:
            return FechaNormalizada(fecha, "aaaa-mm-dd", False), None
        return None, f"«{texto}» tiene una fecha que no existe en el calendario"

    coincidencia = RE_DMY.match(texto)
    if coincidencia:
        anio, supuesto = _interpretar_anio(int(coincidencia.group("anio")))
        fecha = _armar_fecha(anio, int(coincidencia.group("mes")), int(coincidencia.group("dia")))
        if fecha:
            formato = "dd/mm/aa" if supuesto else "dd/mm/aaaa"
            return FechaNormalizada(fecha, formato, supuesto), None
        return None, f"«{texto}» tiene una fecha que no existe en el calendario"

    coincidencia = RE_TEXTO_MES.match(texto)
    if coincidencia:
        mes = MESES_EN_TEXTO.get(normalizar_texto(coincidencia.group("mes")))
        if mes is None:
            return None, f"«{texto}» tiene un mes en palabras que no conozco"
        fecha = _armar_fecha(int(coincidencia.group("anio")), mes, int(coincidencia.group("dia")))
        if fecha:
            return FechaNormalizada(fecha, "dd de <mes> aaaa", False), None
        return None, f"«{texto}» tiene una fecha que no existe en el calendario"

    return None, f"«{texto}» no parece una fecha en ninguno de los formatos conocidos"


def _armar_fecha(anio: int, mes: int, dia: int) -> date | None:
    try:
        return date(anio, mes, dia)
    except ValueError:
        return None


# ================================================================================================
# Horas
# ================================================================================================

RE_HORA = re.compile(
    r"^(?P<hora>\d{1,2})[:.](?P<minuto>\d{2})\s*(?P<meridiano>[ap]\.?\s?m\.?)?$",
    re.IGNORECASE,
)


def normalizar_hora(valor: object) -> tuple[time | None, str | None]:
    """De `"2:30 PM"` a `14:30`, aceptando también `"08:30"` y `"08:00 AM"`.

    En una misma columna conviven 24h y 12h con AM/PM. Se detecta el meridiano cuando está y, si
    no está, se interpreta la hora como 24h, que es el caso mayoritario de la planilla.
    """
    if valor is None:
        return None, "celda vacía"
    if isinstance(valor, time):
        return valor, None
    if isinstance(valor, date):
        return None, "la celda tiene una fecha donde debería haber una hora"

    texto = _colapsar(str(valor).strip())
    if not texto:
        return None, "celda vacía"

    coincidencia = RE_HORA.match(texto)
    if coincidencia is None:
        return None, f"«{texto}» no parece una hora"

    hora = int(coincidencia.group("hora"))
    minuto = int(coincidencia.group("minuto"))
    meridiano = (coincidencia.group("meridiano") or "").replace(".", "").replace(" ", "").lower()

    if meridiano:
        if not 1 <= hora <= 12:
            return None, f"«{texto}» dice AM/PM pero la hora no está entre 1 y 12"
        if meridiano == "pm" and hora != 12:
            hora += 12
        elif meridiano == "am" and hora == 12:
            hora = 0

    if not 0 <= hora <= 23 or minuto > 59:
        return None, f"«{texto}» no es una hora del día"
    return time(hora, minuto), None


# ================================================================================================
# Montos
# ================================================================================================

MONEDA_PESO = "ARS"
MONEDA_DOLAR = "USD"

RE_MONEDA = re.compile(r"(u\s*\$|us\s*\$|usd|d[oó]lar)", re.IGNORECASE)
RE_SIMBOLO_PESO = re.compile(r"[$]")
RE_NO_NUMERICO = re.compile(r"[^\d.,]")


@dataclass(frozen=True)
class Monto:
    """Un monto ya parseado, en la moneda en la que estaba escrito.

    `moneda` va explícita porque la planilla tiene pesos y dólares mezclados y convertirlos entre sí
    necesita un tipo de cambio que el cliente todavía no dio (AGENTS.md §6).
    """

    valor: Decimal
    moneda: str

    @property
    def es_extranjera(self) -> bool:
        return self.moneda != MONEDA_PESO


def normalizar_monto(valor: object) -> tuple[Monto | None, str | None]:
    """De `"$ 11.000,00"` a `11000.00` y de `"18.000,50"` a `18000.50`.

    Resuelve el separador argentino (punto de miles, coma decimal) mirando cuál de los dos
    separadores aparece más a la derecha, que es el que en un número argentino siempre es el
    decimal. `"$12.500"` queda en 12500 y `"0.5"` en 0.5 porque con un solo punto se decide por
    la cantidad de dígitos que le siguen.

    Los valores escritos en dólares se devuelven con `moneda="USD"` y **no** se convierten: falta el
    tipo de cambio, así que corresponde confirmarlo con el cliente.
    """
    if valor is None:
        return None, "celda vacía"
    if isinstance(valor, (int, float, Decimal)):
        return Monto(Decimal(str(valor)), MONEDA_PESO), None

    texto = _colapsar(str(valor).strip())
    if not texto:
        return None, "celda vacía"

    es_dolar = bool(RE_MONEDA.search(texto))
    if es_dolar:
        texto = RE_MONEDA.sub("", texto)
    texto = RE_SIMBOLO_PESO.sub("", texto)

    numero = _parsear_decimal_argentino(texto)
    if numero is None:
        return None, f"«{valor}» no tiene un número reconocible"
    return Monto(numero, MONEDA_DOLAR if es_dolar else MONEDA_PESO), None


def _parsear_decimal_argentino(texto: str) -> Decimal | None:
    """Aplica el criterio de separadores argentinos y devuelve el número."""
    limpio = RE_NO_NUMERICO.sub("", texto).strip()
    if not limpio:
        return None

    tiene_punto = "." in limpio
    tiene_coma = "," in limpio

    if tiene_punto and tiene_coma:
        # El separador decimal es el de la derecha; el otro es de miles.
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif tiene_coma:
        limpio = limpio.replace(".", "").replace(",", ".")
    elif tiene_punto:
        partes = limpio.split(".")
        if len(partes) > 2:
            limpio = "".join(partes)
        elif len(partes[-1]) == 3:
            # Un punto solo con 3 dígitos detrás es de miles: "12.500" son 12500.
            limpio = "".join(partes)
        # Si no, el punto ya es el decimal y queda como está.

    limpio = limpio.replace(",", ".")
    if limpio.count(".") > 1:
        partes = limpio.split(".")
        limpio = "".join(partes[:-1]) + "." + partes[-1]

    try:
        return Decimal(limpio)
    except InvalidOperation:
        return None


def normalizar_decimal_argentino(valor: object) -> tuple[Decimal | None, str | None]:
    """Para números que no son moneda (`Km_Recorridos`): `"35,5"` → `35.5`."""
    if valor is None:
        return None, "celda vacía"
    if isinstance(valor, (int, float, Decimal)):
        return Decimal(str(valor)), None
    texto = _colapsar(str(valor).strip())
    if not texto:
        return None, "celda vacía"
    numero = _parsear_decimal_argentino(texto)
    if numero is None:
        return None, f"«{valor}» no tiene un número reconocible"
    return numero, None


# ================================================================================================
# Capacidad de carga
# ================================================================================================

RE_UNIDAD_CARGA = re.compile(r"(?P<unidad>[a-zA-Z]+)")


@dataclass(frozen=True)
class Capacidad:
    """Capacidad de carga normalizada a kilogramos."""

    kilos: Decimal
    unidad_original: str | None
    unidad_supuesta: bool


def normalizar_capacidad(valor: object) -> tuple[Capacidad | None, str | None]:
    """De `"3,5 toneladas"` a `3500` kg. Mezcla `kg`, `tn` y celdas sin unidad.

    Cuando la celda no trae unidad se asume kg (la unidad de todas las celdas que sí la traen) y
    se marca `unidad_supuesta` para que aparezca en el reporte.
    """
    if valor is None:
        return None, "celda vacía"
    if isinstance(valor, (int, float, Decimal)):
        return Capacidad(Decimal(str(valor)), None, True), None

    texto = _colapsar(str(valor).strip()).lower()
    if not texto:
        return None, "celda vacía"

    coincidencia = RE_UNIDAD_CARGA.search(texto)
    unidad = coincidencia.group("unidad") if coincidencia else None

    if unidad is None:
        numero, motivo = normalizar_decimal_argentino(texto)
        if numero is None:
            return None, motivo
        return Capacidad(kilos=numero, unidad_original=None, unidad_supuesta=True), None

    factor = cat.FACTORES_UNIDAD_CARGA.get(unidad.rstrip("."))
    if factor is None:
        numero, motivo = normalizar_decimal_argentino(texto)
        if numero is None:
            return None, motivo
        return None, f"«{valor}» tiene la unidad «{unidad}» que no conozco"

    solo_numero = texto[: coincidencia.start()].strip() or texto
    numero, motivo = normalizar_decimal_argentino(solo_numero)
    if numero is None:
        return None, motivo
    return Capacidad(kilos=numero * factor, unidad_original=unidad, unidad_supuesta=False), None


# ================================================================================================
# Catálogos
# ================================================================================================


def normalizar_tipo_vehiculo(valor: object) -> tuple[str | None, str | None]:
    """De `"Furgon Grande"` / `"camioneta"` a un valor de `TIPOS_VEHICULO_CANONICOS`.

    El catálogo es provisional (ver `catalogos.py`). Un tipo que no está en la tabla de alias
    devuelve `None` y queda para revisión, no se lo fuerza al más parecido.
    """
    if valor is None:
        return None, "celda vacía"
    clave = normalizar_texto(_colapsar(str(valor).strip()))
    if not clave:
        return None, "celda vacía"
    canonico = cat.ALIAS_TIPO_VEHICULO.get(clave)
    if canonico is None:
        return None, f"«{valor}» no está en el catálogo de tipos de vehículo"
    return canonico, None


def normalizar_estado_movil(valor: object) -> tuple[str | None, str | None, str | None]:
    """De `"En taller hasta el martes"` a un estado canónico, conservando el texto original.

    Devuelve `(estado, texto_original, motivo_de_revision)`. El texto libre original nunca se
    descarta: es la única fuente de por qué un móvil estaba parado, y se guarda como observación.
    """
    if valor is None:
        return None, None, "celda vacía"
    texto = _colapsar(str(valor).strip())
    if not texto:
        return None, None, "celda vacía"

    clave = normalizar_texto(texto)
    if clave in cat.ESTADOS_AMBIGUOS:
        return (
            cat.ESTADOS_AMBIGUOS[clave],
            texto,
            (
                f"«{texto}» admite más de una lectura (disponible / ocupado / inactivo). "
                f"Se mapeó provisionalmente a «{cat.ESTADOS_AMBIGUOS[clave]}» y el texto "
                "original queda como observación."
            ),
        )
    estado = cat.ALIAS_ESTADO_MOVIL.get(clave)
    if estado is None:
        return None, texto, f"«{texto}» no está en el catálogo de estados"
    return estado, texto, None


def normalizar_condicion_iva(valor: object) -> tuple[str | None, str | None]:
    """De `"Resp. Inscripto"` a `"Responsable Inscripto"`.

    Se normaliza aunque la columna no tenga destino en el modelo todavía: queda en el reporte para
    cuando se implemente H2, sin perder el dato original.
    """
    if valor is None:
        return None, "celda vacía"
    clave = normalizar_texto(_colapsar(str(valor).strip()))
    if not clave:
        return None, "celda vacía"
    canonico = cat.ALIAS_CONDICION_IVA.get(clave)
    if canonico is None:
        return None, f"«{valor}» no está en el catálogo de condiciones de IVA"
    return canonico, None


# ================================================================================================
# Bultos
# ================================================================================================

RE_NUMEROS = re.compile(r"\d+")

#: Palabras con las que la celda describe un servicio o un tipo de cosa y no una cantidad de bultos.
INDICADORES_SERVICIO_NO_BULTOS = (
    "sonido",
    "luces",
    "mudanza",
    "depto",
    "departamento",
    "electrodomestico",
    "lavadora",
)


@dataclass(frozen=True)
class Bultos:
    """Cantidad de bultos cuando la celda efectivamente la dice."""

    cantidad: int | None
    es_texto_libre: bool


def normalizar_bultos(valor: object) -> tuple[Bultos, str | None]:
    """De `"6 muebles embalados"` a `6`, pero de `"Archivadores pesados"` a `None`.

    Solo se extrae el número cuando la celda tiene **un único** número: `"10 cajas y 1 heladera"`
    tiene dos y no se sabe si los bultos son 10, 1 o 11, así que no se saca ninguno. Cuando la
    celda describe directamente un servicio (`"Sonido y luces"`) se marca aparte, porque ni
    siquiera es una cantidad de bultos lo que el administrador anotó ahí.
    """
    if valor is None:
        return Bultos(None, False), "celda vacía"
    texto = _colapsar(str(valor).strip())
    if not texto:
        return Bultos(None, False), "celda vacía"

    numeros = [int(n) for n in RE_NUMEROS.findall(texto)]
    if not numeros:
        clave = normalizar_texto(texto)
        describe_servicio = any(indicador in clave for indicador in INDICADORES_SERVICIO_NO_BULTOS)
        if describe_servicio:
            return Bultos(None, True), (
                f"«{texto}» describe un servicio, no una cantidad de bultos. No se extrajo ningún "
                "número."
            )
        return Bultos(None, True), f"«{texto}» no dice cuántos bultos son"

    if len(numeros) > 1:
        return Bultos(None, True), (
            f"«{texto}» tiene {len(numeros)} cantidades ({', '.join(str(n) for n in numeros)}) "
            "y no se sabe cuál es la cantidad de bultos. No se suman ni se elige una."
        )

    return Bultos(numeros[0], False), None


# ================================================================================================
# Estado de cobro
# ================================================================================================


@dataclass(frozen=True)
class Cobro:
    """Lo que se pudo descomponer del texto libre de `Estado_Cobro`.

    Los tres conceptos vienen mezclados en una sola celda. Lo que no se reconoce con confianza
    queda en `None` y el motivo va a revisión humana.
    """

    medio: str | None
    estado: str | None
    saldo: Decimal | None
    monto_original: Decimal | None


def descomponer_estado_cobro(
    valor: object, monto_cobrado: Decimal | None
) -> tuple[Cobro, list[str]]:
    """Separa medio de pago, estado y saldo a partir del texto libre de `Estado_Cobro`.

    Devuelve `(cobro, motivos_de_revision)`. El saldo **solo** se calcula en dos casos: cuando el
    texto dice que el cobro está completo (saldo 0), o cuando dice explícitamente cuánto se pagó
    antes (`"Seña $5000 debe el resto"`, `"Seña 50%"`). En cualquier otro caso queda en `None`:
    adivinar el saldo pendiente de un cliente es el tipo de dato que después alguien va a cobrar.
    """
    motivos: list[str] = []
    if valor is None:
        return Cobro(None, None, None, monto_cobrado), ["celda vacía"]

    texto = _colapsar(str(valor).strip())
    clave = normalizar_texto(texto)
    if not clave:
        return Cobro(None, None, None, monto_cobrado), ["celda vacía"]

    if clave in cat.COBROS_AMBIGUOS:
        motivos.append(f"«{texto}»: {cat.COBROS_AMBIGUOS[clave]}")

    medio = _primer_patron(clave, cat.PATRONES_MEDIO_PAGO)
    estado = _detectar_estado_cobro(clave)

    if medio is None:
        motivos.append(
            f"«{texto}» no dice con qué medio se cobró. No se fuerza a Efectivo ni a Transferencia."
        )
    if estado is None:
        motivos.append(
            f"«{texto}» no dice si el cobro quedó completo, a medias o pendiente. No se asume, así "
            "que el saldo queda sin calcular."
        )

    saldo = _calcular_saldo(clave, texto, monto_cobrado, estado)

    return Cobro(medio=medio, estado=estado, saldo=saldo, monto_original=monto_cobrado), motivos


def _detectar_estado_cobro(clave: str) -> str | None:
    """Estado del cobro, evaluando **parcial y pendiente antes que cobrado**.

    `"Pagó mitad resta factura"` dice "pagó" pero no es un cobro completo: por eso la lista de
    "cobrado" no incluye la raíz `pago` suelta y el orden pone lo específico primero.
    """
    if _coincide_alguno(clave, cat.PATRONES_ESTADO_PARCIAL):
        return cat.COBRO_PARCIAL
    if _coincide_alguno(clave, cat.PATRONES_ESTADO_PENDIENTE):
        return cat.COBRO_PENDIENTE
    if _coincide_alguno(clave, cat.PATRONES_ESTADO_COBRADO):
        return cat.COBRO_COBRADO
    return None


def _coincide_alguno(clave: str, patrones: tuple[str, ...]) -> bool:
    return any(patron in clave for patron in patrones)


def _primer_patron(clave: str, patrones: tuple[tuple[str, str], ...]) -> str | None:
    for patron, valor in patrones:
        if patron in clave:
            return valor
    return None


def _calcular_saldo(
    clave: str, texto: str, monto: Decimal | None, estado: str | None
) -> Decimal | None:
    if estado is None:
        return None

    if estado == cat.COBRO_COBRADO:
        return Decimal(0)

    if estado == cat.COBRO_PENDIENTE:
        return monto

    # Estado parcial: el saldo solo existe si la celda dice cuánto se pagó antes.
    if monto is None:
        return None
    monto_sena, es_porcentaje = _monto_de_sena(texto)
    if monto_sena is None:
        return None
    if es_porcentaje:
        return (monto * (Decimal(100) - monto_sena) / Decimal(100)).quantize(Decimal("0.01"))
    return monto - monto_sena


#: Busca `seña` aunque venga con tilde o sin ella, y en cualquier mayúscula. El `ñ` tiene que estar
#: en la clase de caracteres: con un `n?` literal la palabra acentuada de la planilla no matcheaba
#: y el monto de la seña se perdía en silencio.
RE_SENA = re.compile(r"s[eé][nñ]?[aá]", re.IGNORECASE)


def _monto_de_sena(texto: str) -> tuple[Decimal | None, bool]:
    """Saca el monto de la seña: puede ser un porcentaje (`"50%"`) o un importe (`"$5000"`)."""
    coincidencia_pct = re.search(r"(\d+(?:[.,]\d+)?)\s*%", texto)
    if coincidencia_pct:
        numero, _ = normalizar_decimal_argentino(coincidencia_pct.group(1))
        return (numero, True) if numero is not None else (None, True)

    coincidencia_sena = RE_SENA.search(texto)
    if coincidencia_sena is None:
        return None, False
    numeros = RE_NUMEROS.findall(texto[coincidencia_sena.end() :])
    if not numeros:
        return None, False
    numero, _ = normalizar_decimal_argentino(numeros[0])
    return (numero, False) if numero is not None else (None, False)


# ================================================================================================
# Direcciones
# ================================================================================================


def es_direccion_no_estructurada(valor: object) -> bool:
    """True si el campo es una instrucción de retiro y no una dirección postal.

    El `Cliente` de H1 exige `direccion_habitual` entre 5 y 250 caracteres pero no tiene forma de
    marcar que el texto no es una dirección, así que estos valores entran igual y quedan reportados
    como gap.
    """
    if valor is None:
        return False
    clave = normalizar_texto(_colapsar(str(valor).strip()))
    return any(indicador in clave for indicador in cat.INDICADORES_DIRECCION_NO_ESTRUCTURADA)
