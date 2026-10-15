"""Generación del reporte Markdown de la migración.

El reporte es el entregable que convierte "la migración corrió" en "acá está qué mirar". Tiene
secciones separadas a propósito (FR-034): las transformaciones aplicadas son el resultado normal de
la historia, y los casos de revisión humana **no** — son decisiones que la migración no tomó y que
salen de la spec, no del código (AGENTS.md §5, §6).

Este módulo solo arma texto. No lee el Excel ni toca la base.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from scripts.migracion.carga import ResultadoCarga
from scripts.migracion.extraccion import resumen_de_catalogos
from scripts.migracion.revision import Gravedad, RevisionHumana
from scripts.migracion.transformacion import (
    COLUMNAS_SIN_MAPEO_CLIENTE,
    ClienteMigrable,
    Movil,
    Viaje,
)

RUTA_REPORTE_POR_DEFECTO = "data/reporte_migracion.md"

#: Descripción de cada transformación aplicada. Se escribe a mano porque es la explicación de por
#: qué se normaliza así, y una explicación no se puede derivar del código sin repetirla.
TRANSFORMACIONES: tuple[tuple[str, str, str, str], ...] = (
    (
        "Choferes_y_Moviles",
        "`Cod_Movil`",
        "`MOV-01`",
        "Se normaliza a `MOV-00`, aceptando el número con o sin prefijo, con o sin guion y con "
        'ceros de relleno: `"MOV-01"`, `"MOV01"` y `"03"` son el mismo código.',
    ),
    (
        "Choferes_y_Moviles",
        "`Nombre_Chofer`",
        "minúsculas, sin acentos",
        "Solo para comparar. El nombre que se muestra se conserva tal como está escrito.",
    ),
    (
        "Choferes_y_Moviles",
        "`Telefono_Contacto`",
        "solo dígitos",
        "Se quitan `+`, espacios y guiones. Las anotaciones que no son un teléfono quedan en "
        "`NULL`. No se decide cómo se guardan los teléfonos con código de país: esa regla sigue "
        "abierta.",
    ),
    (
        "Choferes_y_Moviles",
        "`Tipo_Vehiculo`",
        "catálogo fijo",
        "Se resuelve contra un catálogo de tipos de vehículo. Un valor fuera del catálogo queda "
        "sin normalizar y se reporta, sin forzar el más parecido.",
    ),
    (
        "Choferes_y_Moviles",
        "`Capacidad_Carga`",
        "kilogramos",
        "`kg`, `kgs`, `kilo(s)` valen 1; `tn`, `t`, `ton(s)`, `tonelada(s)` valen 1000. Las "
        "celdas sin unidad se asumen en kg y se reportan como supuesto.",
    ),
    (
        "Choferes_y_Moviles",
        "`Tarifa_Hora_Base`, `Tarifa_Km_Excedente`",
        "decimal con moneda explícita",
        "Se resuelve el separador argentino (punto de miles, coma decimal). Los valores en dólares "
        "conservan su moneda y **no** se convierten: falta el tipo de cambio.",
    ),
    (
        "Choferes_y_Moviles",
        "`Estado_Actual`",
        "`disponible` / `ocupado` / `inactivo`",
        "Se mapea al enum reducido y el texto original se conserva como observación. Los textos "
        "que admiten más de una lectura se mapean a un estado provisional y se reportan.",
    ),
    (
        "Clientes_Cotizaciones",
        "`ID_Cliente`",
        "`CLI-000`",
        "Se normaliza el prefijo para poder detectar filas repetidas. **No** se usa como `id`: "
        "`Cliente` genera el suyo.",
    ),
    (
        "Clientes_Cotizaciones",
        "`Nombre_o_Empresa`",
        "minúsculas, sin acentos",
        "Solo para comparar contra `razon_social_key`, que es el `UNIQUE` de H1 (DD-2). El texto "
        "que se muestra no se toca.",
    ),
    (
        "Clientes_Cotizaciones",
        "`Telefono`",
        "solo dígitos",
        "Igual que el de los choferes.",
    ),
    (
        "Clientes_Cotizaciones",
        "`Direccion_Habitual`",
        "sin cambios",
        "Se conserva tal cual. Los valores que no son una dirección postal (por ejemplo una "
        "instrucción de retiro) se marcan, porque `Cliente` no tiene forma de distinguirlos.",
    ),
    (
        "Clientes_Cotizaciones",
        "`Condicion_IVA`",
        "catálogo fijo",
        "Se resuelve contra `Responsable Inscripto` / `Consumidor Final` / `Exento`. No tiene "
        "destino en el modelo todavía, pero se normaliza para cuando exista.",
    ),
    (
        "Clientes_Cotizaciones",
        "`Historial_Pagos`",
        "sin cambios",
        "Es una nota en palabras, no un dato estructurado. **No** se traduce a "
        "`tiene_cuenta_corriente` ni a nada más: ese campo queda siempre en `false`.",
    ),
    (
        "Registro_Viajes",
        "`Nro_Viaje`",
        "`VJ-0000`",
        "Mismo criterio que `Cod_Movil`, con ancho de 4 dígitos.",
    ),
    (
        "Registro_Viajes",
        "`Fecha_Servicio`",
        "fecha ISO",
        "Se prueban los cuatro formatos contra cada celda y gana el que encaja, así que el formato "
        "se detecta por contenido y no por posición de columna. Los años de dos dígitos se "
        "proyectan al siglo XXI y se reportan como supuesto.",
    ),
    (
        "Registro_Viajes",
        "`Hora_Inicio`, `Hora_Fin`",
        "24 horas",
        "Se reconoce el formato 12 horas con AM/PM cuando está escrito. Una hora con AM/PM fuera "
        "del rango 1-12 se rechaza en vez de 'corregirse'.",
    ),
    (
        "Registro_Viajes",
        "`Km_Recorridos`",
        "decimal con punto",
        "Se resuelve la coma decimal argentina.",
    ),
    (
        "Registro_Viajes",
        "`Bultos_Estimados`",
        "entero o `NULL`",
        "Solo se extrae la cantidad cuando hay **exactamente un** número. Sin número, con más de "
        "uno, o cuando la celda describe un servicio, queda en `NULL` y el texto se conserva.",
    ),
    (
        "Registro_Viajes",
        "`Monto_Cobrado`",
        "decimal con moneda explícita",
        "Igual que las tarifas. Los dólares no se convierten.",
    ),
    (
        "Registro_Viajes",
        "`Estado_Cobro`",
        "medio de pago + estado + saldo",
        "La celda mezcla tres conceptos y se separan por palabras clave. Se evalúa como parcial o "
        "pendiente **antes** que como cobrado, para que un texto que dice 'pagó' sin decir 'pagó "
        "todo' no cuente como cobro completo. El saldo solo se calcula cuando el texto lo dice.",
    ),
)


@dataclass
class DatosReporte:
    """Todo lo que el reporte necesita. Se arma en el `__main__` y se pasa entero."""

    clientes: list[ClienteMigrable]
    moviles: list[Movil]
    viajes: list[Viaje]
    carga: ResultadoCarga
    casos: list[RevisionHumana] = field(default_factory=list)
    archivo_origen: str = ""
    generado_en: date | None = None


def _tabla_encabezados() -> list[str]:
    return ["| Hoja | Columna | Normalización | Criterio |", "| --- | --- | --- | --- |"]


def _seccion_transformaciones() -> list[str]:
    filas = _tabla_encabezados()
    filas.extend(
        f"| {hoja} | {columna} | {resultado} | {criterio} |"
        for hoja, columna, resultado, criterio in TRANSFORMACIONES
    )
    return filas


def _seccion_cataligos() -> list[str]:
    return [
        "Los catálogos que usó la migración **no están confirmados por el cliente** (DP-01). Se "
        "armaron a partir de los valores que aparecen en la planilla.",
        "",
        *[f"- {linea}" for linea in resumen_de_catalogos()],
        "",
        "Cuando la historia que modele cada entidad (H4 para choferes y vehículos, H10 para pagos) "
        "defina su catálogo propio, estos valores se reemplazan por los de esa spec.",
    ]


def _seccion_revision(casos: list[RevisionHumana]) -> list[str]:
    if not casos:
        return [
            "No quedó ningún caso para revisar: todas las filas del archivo se pudieron "
            "convertir sin decisiones pendientes."
        ]

    bloqueantes = [caso for caso in casos if caso.gravedad is Gravedad.BLOQUEANTE]
    a_confirmar = [caso for caso in casos if caso.gravedad is Gravedad.A_CONFIRMAR]

    lineas = [
        f"Quedaron **{len(casos)} casos** para que una persona los resuelva. Cada uno cita la "
        "hoja, el número de fila del Excel y el valor que había, para poder buscarlo en la "
        "planilla.",
        "",
    ]

    if bloqueantes:
        lineas += [
            f"## Bloqueantes ({len(bloqueantes)})",
            "",
            "Estos casos impiden que el dato llegue a su destino con un valor confiable. Hay que "
            "resolverlos antes de que la base sea la fuente de verdad.",
            "",
            "| Hoja | Fila | Clave | Motivo | Valor original | Qué pasó |",
            "| --- | --- | --- | --- | --- | --- |",
            *[caso.como_fila_markdown() for caso in bloqueantes],
            "",
        ]

    if a_confirmar:
        lineas += [
            f"## Para confirmar ({len(a_confirmar)})",
            "",
            "El dato se cargó o se transformó con un supuesto explícito. Conviene revisarlos, pero "
            "no frena la migración.",
            "",
            "| Hoja | Fila | Clave | Motivo | Valor original | Qué pasó |",
            "| --- | --- | --- | --- | --- | --- |",
            *[caso.como_fila_markdown() for caso in a_confirmar],
            "",
        ]

    return lineas


def _seccion_gaps() -> list[str]:
    lineas = [
        "Estas columnas de la planilla **no tienen destino** en el modelo que existe hoy. No se "
        "agregó ninguna columna a las entidades: hacer eso requiere acordarlo con quien implementó "
        "H1, y decidirlo desde una migración no corresponde (AGENTS.md §5).",
        "",
        "| Columna | Por qué no tiene destino | Qué se hizo |",
        "| --- | --- | --- |",
        *[
            f"| `{columna}` | {explicacion} | Se conserva el valor en este reporte. |"
            for columna, explicacion in COLUMNAS_SIN_MAPEO_CLIENTE
        ],
    ]
    return lineas


def _seccion_resumen(datos: DatosReporte) -> list[str]:
    carga = datos.carga
    return [
        "| Conjunto | Registros | Destino | Estado |",
        "| --- | --- | --- | --- |",
        f"| Clientes | {len(datos.clientes)} | tabla `clientes` | "
        f"cargados: **{len(carga.agregados)}**, ya existentes: **{len(carga.ya_existentes)}**, "
        f"omitidos: **{len(carga.omitidos)}** |",
        f"| Móviles / choferes | {len(datos.moviles)} | tabla `choferes` + `vehiculos` | "
        "**pendiente: la tabla no existe** |",
        f"| Viajes / servicios | {len(datos.viajes)} | tabla `servicios` | "
        "**pendiente: la tabla no existe** |",
        f"| Pagos | {len(datos.viajes)} (derivados de `Estado_Cobro`) | tabla `pagos` | "
        "**pendiente: la tabla no existe** |",
        "",
        "Las tres últimas filas no se escribieron. Crear esas tablas implica decidir la máquina de "
        "estados de `Servicio` y el catálogo de medios de pago, que el cliente todavía no confirmó "
        "(AGENTS.md §6). Los datos ya están normalizados y probados: cuando esas historias "
        "existan, solo hay que agregar el módulo de carga correspondiente, sin tocar la "
        "normalización.",
        "",
    ]


def _seccion_omitidos(datos: DatosReporte) -> list[str]:
    if not datos.carga.omitidos:
        return []
    return [
        "## Clientes que no se pudieron cargar",
        "",
        *[f"- **{nombre}**" for nombre in datos.carga.omitidos],
        "",
    ]


def _seccion_historicos_preservados(datos: DatosReporte) -> list[str]:
    """Los textos libres que quedaron como observación, para que nadie busque un dato que sí
    está."""
    filas: list[str] = []

    for movil in datos.moviles:
        for observacion in movil.observaciones:
            filas.append(
                f"- Móvil `{movil.codigo}` ({movil.nombre_chofer}): estado "
                f"`{movil.estado}` — texto original: «{observacion}»"
            )

    for viaje in datos.viajes:
        if viaje.bultos_estimados is None and viaje.bultos_texto_original:
            filas.append(
                f"- Viaje `{viaje.codigo}`: bultos sin cantidad — texto original: "
                f"«{viaje.bultos_texto_original}»"
            )

    if not filas:
        return []

    return [
        "## Textos que se conservaron como observación",
        "",
        "Estos valores se mapearon a un valor de catálogo, pero el texto original queda guardado "
        "porque es la única evidencia de qué quiso decir quien llevaba la planilla.",
        "",
        *filas,
        "",
    ]


def generar_markdown(datos: DatosReporte) -> str:
    """Arma el reporte completo."""
    generado_en = datos.generado_en or date.today()
    bloqueantes = sum(1 for caso in datos.casos if caso.gravedad is Gravedad.BLOQUEANTE)

    secciones: list[str] = [
        "# Reporte de migración de datos históricos",
        "",
        f"- **Archivo de origen**: `{datos.archivo_origen}`",
        f"- **Generado**: {generado_en.isoformat()}",
        f"- **Filas leídas**: {len(datos.clientes)} clientes, {len(datos.moviles)} móviles, "
        f"{len(datos.viajes)} viajes",
        f"- **Casos para revisión humana**: {len(datos.casos)} "
        f"({bloqueantes} bloqueantes, {len(datos.casos) - bloqueantes} para confirmar)",
        "",
        "> Los casos de esta revisión se dejaron **a propósito**: donde el dato era ambiguo, la "
        "migración lo dejó señalado en vez de inventar una regla de negocio (AGENTS.md §6).",
        "",
        "## Resumen",
        "",
        *_seccion_resumen(datos),
        *_seccion_omitidos(datos),
        *_seccion_historicos_preservados(datos),
        "## Transformaciones aplicadas",
        "",
        "Cada fila dice de qué columna sale el dato, cómo queda después y por qué se normaliza "
        "así.",
        "",
        *_seccion_transformaciones(),
        "",
        *_seccion_cataligos(),
        "",
        "## Casos para revisión humana",
        "",
        *_seccion_revision(datos.casos),
        "## Gaps de mapeo",
        "",
        *_seccion_gaps(),
        "",
    ]

    return "\n".join(secciones)


def escribir_reporte(datos: DatosReporte, ruta) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(generar_markdown(datos), encoding="utf-8")
