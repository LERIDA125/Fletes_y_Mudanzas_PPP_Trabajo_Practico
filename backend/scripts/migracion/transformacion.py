"""Transformación: filas del Excel → registros normalizados + cola de revisión humana.

Acá se resuelve cada anomalía conocida de la planilla. La regla general es una sola: **si la
migración no puede decidir con confianza, no decide** — deja el campo en `None` y anota el caso
para que una persona lo resuelva (AGENTS.md §6).

Nada de este módulo escribe en la base: solo produce estructuras. La carga es de `carga.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal

from scripts.migracion import normalizacion as norm
from scripts.migracion.extraccion import Fila
from scripts.migracion.revision import ColaDeRevision, Gravedad, Motivo, RevisionHumana

# ================================================================================================
# Móviles (chofer + vehículo)
# ================================================================================================

#: Campos de la planilla que se comparan entre filas con el mismo código de móvil.
CAMPOS_COMPARABLES_MOVIL: tuple[tuple[str, str], ...] = (
    ("Nombre_Chofer", "nombre del chofer"),
    ("Telefono_Contacto", "teléfono"),
    ("Tipo_Vehiculo", "tipo de vehículo"),
    ("Capacidad_Carga", "capacidad de carga"),
    ("Tarifa_Hora_Base", "tarifa por hora"),
    ("Tarifa_Km_Excedente", "tarifa por km"),
    ("Estado_Actual", "estado"),
)


@dataclass
class Movil:
    """Un móvil (chofer + vehículo) tal como quedó después de normalizar.

    `filas_de_origen` guarda de qué filas del Excel salió: cuando el mismo `codigo` aparece dos
    veces, el registro las lleva para poder mostrar el choque en el reporte.
    """

    codigo: str
    nombre_chofer: str
    nombre_chofer_key: str
    telefono: str | None
    tipo_vehiculo: str | None
    capacidad_kg: Decimal | None
    tarifa_hora_base: Decimal | None
    tarifa_km_excedente: Decimal | None
    moneda_tarifa: str
    estado: str | None
    observaciones: list[str] = field(default_factory=list)
    filas_de_origen: list[int] = field(default_factory=list)


def transformar_moviles(filas: list[Fila]) -> tuple[list[Movil], ColaDeRevision]:
    """Normaliza `Choferes_y_Moviles` y detecta los códigos que aparecen en más de una fila.

    Un `Cod_Movil` repetido casi siempre es el mismo móvil cargado dos veces con un formato
    distinto, no dos móviles distintos. Cuál de las dos filas manda **no** se decide acá: se
    conserva la primera como provisional y se reportan todas las diferencias para que alguien
    confirme cuál es la vigente.
    """
    cola = ColaDeRevision()
    por_codigo: dict[str, Movil] = {}
    filas_por_codigo: dict[str, list[Fila]] = {}

    for fila in filas:
        codigo = norm.codigo_de_movil(fila.datos.get("Cod_Movil"))
        if codigo is None:
            cola.agregar(
                RevisionHumana(
                    hoja=fila.hoja,
                    fila=fila.numero,
                    clave=f"fila {fila.numero}",
                    motivo=Motivo.DATO_INCOMPLETO,
                    gravedad=Gravedad.BLOQUEANTE,
                    valor_original=str(fila.datos.get("Cod_Movil") or ""),
                    detalle="No se pudo leer el código de móvil, así que la fila no se migró.",
                )
            )
            continue

        clave = codigo.valor
        filas_por_codigo.setdefault(clave, []).append(fila)

        # Todas las filas se normalizan, no solo la que gana. Si una versión duplicada trae un monto
        # en dólares o un teléfono que no es un teléfono, hay que reportarlo igual: la persona que
        # revise tiene que saber que esa celda existe, aunque después no se use. Normalizar solo la
        # primera haría que las anomalías de la segunda desaparecieran del reporte sin dejar rastro.
        movil_normalizado = _movil_desde_fila(fila, clave, cola)
        if clave not in por_codigo:
            por_codigo[clave] = movil_normalizado
        por_codigo[clave].filas_de_origen.append(fila.numero)

    _reportar_duplicados_de_movil(filas_por_codigo, cola)

    return sorted(por_codigo.values(), key=lambda movil: movil.codigo), cola


def _movil_desde_fila(fila: Fila, codigo: str, cola: ColaDeRevision) -> Movil:
    datos = fila.datos
    nombre = str(datos.get("Nombre_Chofer") or "").strip()

    telefono, motivo_telefono = norm.normalizar_telefono(datos.get("Telefono_Contacto"))
    if telefono is None and motivo_telefono:
        _agregar(
            cola,
            fila,
            codigo,
            Motivo.DATO_INCOMPLETO,
            Gravedad.A_CONFIRMAR,
            str(datos.get("Telefono_Contacto") or ""),
            f"El teléfono se guardó vacío porque {motivo_telefono}.",
        )

    tipo, motivo_tipo = norm.normalizar_tipo_vehiculo(datos.get("Tipo_Vehiculo"))
    if tipo is None and motivo_tipo:
        _agregar(
            cola,
            fila,
            codigo,
            Motivo.TEXTO_AMBIGUO,
            Gravedad.BLOQUEANTE,
            str(datos.get("Tipo_Vehiculo") or ""),
            motivo_tipo,
        )

    capacidad, motivo_capacidad = norm.normalizar_capacidad(datos.get("Capacidad_Carga"))
    if capacidad is None and motivo_capacidad:
        _agregar(
            cola,
            fila,
            codigo,
            Motivo.DATO_INCOMPLETO,
            Gravedad.BLOQUEANTE,
            str(datos.get("Capacidad_Carga") or ""),
            motivo_capacidad,
        )
    elif capacidad and capacidad.unidad_supuesta:
        _agregar(
            cola,
            fila,
            codigo,
            Motivo.UNIDAD_IMPLICITA,
            Gravedad.A_CONFIRMAR,
            str(datos.get("Capacidad_Carga") or ""),
            "La celda no dice la unidad: se asumió kg. Si era toneladas, la capacidad quedó 1000 "
            "veces menor.",
        )

    tarifas: dict[str, norm.Monto | None] = {}
    moneda = norm.MONEDA_PESO
    for campo in ("Tarifa_Hora_Base", "Tarifa_Km_Excedente"):
        monto, causa = norm.normalizar_monto(datos.get(campo))
        tarifas[campo] = monto
        if monto is None and causa:
            _agregar(
                cola,
                fila,
                codigo,
                Motivo.DATO_INCOMPLETO,
                Gravedad.BLOQUEANTE,
                str(datos.get(campo) or ""),
                causa,
            )
        elif monto and monto.es_extranjera:
            moneda = norm.MONEDA_DOLAR
            _agregar(
                cola,
                fila,
                codigo,
                Motivo.MONEDA_EXTRANJERA,
                Gravedad.BLOQUEANTE,
                str(datos.get(campo) or ""),
                f"El valor está en dólares ({monto.valor} USD). No se convirtió a pesos: falta que "
                "el cliente confirme el tipo de cambio y desde qué fecha se aplica.",
            )

    estado, texto_estado, motivo_estado = norm.normalizar_estado_movil(datos.get("Estado_Actual"))
    if motivo_estado:
        _agregar(
            cola,
            fila,
            codigo,
            Motivo.TEXTO_AMBIGUO,
            Gravedad.A_CONFIRMAR,
            str(datos.get("Estado_Actual") or ""),
            motivo_estado,
        )

    return Movil(
        codigo=codigo,
        nombre_chofer=nombre,
        nombre_chofer_key=norm.normalizar_texto(nombre),
        telefono=telefono.digitos if telefono else None,
        tipo_vehiculo=tipo,
        capacidad_kg=capacidad.kilos if capacidad else None,
        tarifa_hora_base=tarifas["Tarifa_Hora_Base"].valor if tarifas["Tarifa_Hora_Base"] else None,
        tarifa_km_excedente=(
            tarifas["Tarifa_Km_Excedente"].valor if tarifas["Tarifa_Km_Excedente"] else None
        ),
        moneda_tarifa=moneda,
        estado=estado,
        observaciones=[texto_estado] if texto_estado else [],
    )


def _agregar(
    cola: ColaDeRevision,
    fila: Fila,
    clave: str,
    motivo: Motivo,
    gravedad: Gravedad,
    valor_original: str,
    detalle: str,
) -> None:
    cola.agregar(
        RevisionHumana(
            hoja=fila.hoja,
            fila=fila.numero,
            clave=clave,
            motivo=motivo,
            gravedad=gravedad,
            valor_original=valor_original,
            detalle=detalle,
        )
    )


def _reportar_duplicados_de_movil(
    filas_por_codigo: dict[str, list[Fila]], cola: ColaDeRevision
) -> None:
    """Compara las filas que comparten código y reporta en qué difieren, sin elegir la buena."""
    for codigo, filas in filas_por_codigo.items():
        if len(filas) < 2:
            continue
        primera = filas[0]
        diferencias: list[str] = []
        for fila in filas[1:]:
            for campo, etiqueta in CAMPOS_COMPARABLES_MOVIL:
                valor_a = str(primera.datos.get(campo) or "").strip()
                valor_b = str(fila.datos.get(campo) or "").strip()
                if norm.normalizar_texto(valor_a) != norm.normalizar_texto(valor_b):
                    diferencias.append(
                        f"{etiqueta}: fila {primera.numero} «{valor_a}» vs fila "
                        f"{fila.numero} «{valor_b}»"
                    )
        numeros = ", ".join(str(fila.numero) for fila in filas)
        nombres = "; ".join(str(fila.datos.get("Nombre_Chofer") or "") for fila in filas)
        _agregar(
            cola,
            primera,
            codigo,
            Motivo.DUPLICADO,
            Gravedad.BLOQUEANTE,
            nombres,
            f"El código {codigo} aparece en las filas {numeros} del Excel, con nombres "
            f"«{nombres}». "
            "Se trataron como el mismo móvil con dos versiones y se conservó la primera fila como "
            "provisional; NO se decidió cuál es la vigente"
            + (f". Difieren en: {'; '.join(diferencias)}." if diferencias else "."),
        )


# ================================================================================================
# Clientes
# ================================================================================================

#: Columnas de `Clientes_Cotizaciones` que no tienen destino en el `Cliente` de H1. Se listan acá
#: para que el reporte las nombre todas juntas y no se pierda ninguna.
COLUMNAS_SIN_MAPEO_CLIENTE: tuple[tuple[str, str], ...] = (
    (
        "ID_Cliente",
        "El `Cliente` de H1 genera su propio `id` con identity y no guarda el código de "
        "la planilla. No se forzó un id ni se agregó una columna.",
    ),
    ("Localidad_Barrio", "No existe un campo de localidad ni de barrio en el `Cliente` de H1."),
    (
        "Condicion_IVA",
        "Los datos fiscales están explícitamente fuera del alcance de H1 (se "
        "agrupan en H2). La columna sí se normalizó, a un catálogo de tres valores.",
    ),
    (
        "Historial_Pagos",
        "No hay ningún campo de historial de pagos. Es una nota en palabras, no un "
        "dato estructurado, así que no se tradujo a `tiene_cuenta_corriente` ni a "
        "ninguna otra cosa.",
    ),
)


@dataclass
class ClienteMigrable:
    """Un cliente listo para cargarse con `ClienteRepo`.

    Solo lleva los cuatro campos que H1 definió. Lo que no entra ahí se conserva en campos aparte
    para el reporte: no se inventa una columna nueva en la entidad para acomodarlo.
    """

    nombre: str
    nombre_key: str
    telefono: str | None
    direccion: str
    direccion_es_estructurada: bool
    codigo_origen: str
    localidad_barrio: str | None
    condicion_iva: str | None
    historial_pagos: str | None
    fila_origen: int
    hoja_origen: str


def transformar_clientes(filas: list[Fila]) -> tuple[list[ClienteMigrable], ColaDeRevision]:
    """Normaliza `Clientes_Cotizaciones` a los cuatro campos que el `Cliente` de H1 define.

    `tiene_cuenta_corriente` queda **siempre en `False`**: `Historial_Pagos` es una nota en
    palabras ("Fiado de palabra", "Paga a 30 días") y traducirla a un booleano sería inventar la
    política de cuenta corriente, que es una de las decisiones que el cliente todavía no tomó
    (AGENTS.md §6). El texto se conserva íntegro para cuando se defina la regla.
    """
    cola = ColaDeRevision()
    clientes: list[ClienteMigrable] = []
    vistos: dict[str, ClienteMigrable] = {}
    columnas_sin_mapeo: dict[str, list[tuple[int, object]]] = {}

    for fila in filas:
        codigo = norm.codigo_de_cliente(fila.datos.get("ID_Cliente"))
        nombre = str(fila.datos.get("Nombre_o_Empresa") or "").strip()
        clave = codigo.valor if codigo else norm.normalizar_texto(nombre)

        if not nombre:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DATO_INCOMPLETO,
                Gravedad.BLOQUEANTE,
                "(vacío)",
                "El nombre del cliente está vacío, así que la fila no se migró.",
            )
            continue

        if clave in vistos:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DUPLICADO_EN_ARCHIVO,
                Gravedad.BLOQUEANTE,
                nombre,
                f"La fila {fila.numero} repite el cliente ya visto en la fila "
                f"{vistos[clave].fila_origen} ({nombre}). Solo se conservó la primera.",
            )
            continue

        telefono, motivo_telefono = norm.normalizar_telefono(fila.datos.get("Telefono"))
        if telefono is None:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DATO_INCOMPLETO,
                Gravedad.BLOQUEANTE,
                str(fila.datos.get("Telefono") or ""),
                f"El teléfono es obligatorio en el `Cliente` de H1 y {motivo_telefono}. La fila no "
                "se puede cargar hasta que se complete.",
            )

        direccion = str(fila.datos.get("Direccion_Habitual") or "").strip()
        direccion_estructurada = not norm.es_direccion_no_estructurada(direccion)
        if not direccion_estructurada:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DIRECCION_NO_ESTRUCTURADA,
                Gravedad.BLOQUEANTE,
                direccion,
                f"«{direccion}» no es una dirección postal sino una instrucción de retiro. El "
                "`Cliente` de H1 exige `direccion_habitual` y no tiene forma de marcar que el "
                "texto no es una dirección, así que se conservó tal cual. Hay que acordarlo con "
                "quien hizo H1: agregar un campo, o aceptar el texto libre con una convención.",
            )

        condicion_iva, motivo_iva = norm.normalizar_condicion_iva(fila.datos.get("Condicion_IVA"))
        if motivo_iva:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.SIN_MAPEO_EN_MODELO,
                Gravedad.A_CONFIRMAR,
                str(fila.datos.get("Condicion_IVA") or ""),
                f"La condición de IVA no se pudo normalizar: {motivo_iva}",
            )

        for columna, _ in COLUMNAS_SIN_MAPEO_CLIENTE:
            columnas_sin_mapeo.setdefault(columna, []).append(
                (fila.numero, fila.datos.get(columna))
            )

        cliente = ClienteMigrable(
            nombre=nombre,
            nombre_key=norm.normalizar_texto(nombre),
            telefono=telefono.digitos if telefono else None,
            direccion=direccion,
            direccion_es_estructurada=direccion_estructurada,
            codigo_origen=str(fila.datos.get("ID_Cliente") or "").strip(),
            localidad_barrio=str(fila.datos.get("Localidad_Barrio") or "").strip() or None,
            condicion_iva=condicion_iva,
            historial_pagos=str(fila.datos.get("Historial_Pagos") or "").strip() or None,
            fila_origen=fila.numero,
            hoja_origen=fila.hoja,
        )
        clientes.append(cliente)
        vistos[clave] = cliente

    _reportar_columnas_sin_mapeo(columnas_sin_mapeo, filas[0].hoja if filas else "", cola)
    return clientes, cola


def _reportar_columnas_sin_mapeo(
    columnas: dict[str, list[tuple[int, object]]], hoja: str, cola: ColaDeRevision
) -> None:
    """Una revisión por columna sin destino, en vez de una por celda: el reporte queda legible."""
    numeros = (numero for valores in columnas.values() for numero, _ in valores)
    fila_ejemplo = min(numeros, default=1)
    for columna, explicacion in COLUMNAS_SIN_MAPEO_CLIENTE:
        valores = columnas.get(columna)
        if not valores:
            continue
        filas_afectadas = ", ".join(str(numero) for numero, _ in valores)
        cola.agregar(
            RevisionHumana(
                hoja=hoja,
                fila=fila_ejemplo,
                clave=f"columna `{columna}`",
                motivo=Motivo.SIN_MAPEO_EN_MODELO,
                gravedad=Gravedad.A_CONFIRMAR,
                valor_original=f"{len(valores)} celdas (filas {filas_afectadas})",
                detalle=f"{explicacion} No se agregó la columna ni se descartó el valor.",
            )
        )


# ================================================================================================
# Viajes
# ================================================================================================


@dataclass
class Viaje:
    """Un viaje de `Registro_Viajes` normalizado.

    `servicio_id` y `pago_id` quedan en `None` a propósito: las tablas `servicios` y `pagos`
    todavía no existen, así que este registro es resultado de la transformación pero no tiene
    destino posible todavía.
    """

    codigo: str
    fecha: date
    fecha_formato_origen: str
    chofer_nombre: str
    chofer_nombre_key: str
    cliente_nombre: str
    cliente_nombre_key: str
    origen: str
    destino: str
    hora_inicio: time | None
    hora_fin: time | None
    km_recorridos: Decimal | None
    bultos_estimados: int | None
    bultos_texto_original: str
    monto_cobrado: Decimal | None
    moneda_monto: str
    pago_medio: str | None
    pago_estado: str | None
    pago_saldo: Decimal | None
    fila_origen: int
    hoja_origen: str
    movil_codigo: str | None = None
    servicio_id: int | None = None
    pago_id: int | None = None


def transformar_viajes(filas: list[Fila]) -> tuple[list[Viaje], ColaDeRevision]:
    """Normaliza `Registro_Viajes`. Los nombres de chofer y cliente se conservan como texto.

    No se inventan claves foráneas: con `choferes` y `servicios` sin definir no hay contra qué
    resolver el nombre del chofer o del cliente de la fila. Las claves normalizadas quedan en el
    registro para que el cruce se haga cuando esas tablas existan.
    """
    cola = ColaDeRevision()
    viajes: list[Viaje] = []
    vistos: dict[str, int] = {}

    for fila in filas:
        codigo = norm.codigo_de_viaje(fila.datos.get("Nro_Viaje"))
        if codigo is None:
            _agregar(
                cola,
                fila,
                f"fila {fila.numero}",
                Motivo.DATO_INCOMPLETO,
                Gravedad.BLOQUEANTE,
                str(fila.datos.get("Nro_Viaje") or ""),
                "No se pudo leer el número de viaje, así que la fila no se migró.",
            )
            continue
        clave = codigo.valor

        if clave in vistos:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DUPLICADO_EN_ARCHIVO,
                Gravedad.BLOQUEANTE,
                str(fila.datos.get("Nro_Viaje") or ""),
                f"El número de viaje {clave} ya apareció en la fila {vistos[clave]}. Solo se "
                "conservó la primera.",
            )
            continue

        fecha, motivo_fecha = norm.normalizar_fecha(fila.datos.get("Fecha_Servicio"))
        if fecha is None:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DATO_INCOMPLETO,
                Gravedad.BLOQUEANTE,
                str(fila.datos.get("Fecha_Servicio") or ""),
                f"No se pudo interpretar la fecha: {motivo_fecha}",
            )
            continue

        if fecha.anio_supuesto:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.SUPUESTO_DE_ANIO,
                Gravedad.A_CONFIRMAR,
                str(fila.datos.get("Fecha_Servicio") or ""),
                f"La fecha «{fila.datos.get('Fecha_Servicio')}» trae un año de dos dígitos y se "
                f"proyectó a {fecha.valor.year} (mismo criterio que `strptime('%y')`). Si algún "
                "viaje fuera de 1900, la proyección lo manda al siglo equivocado.",
            )

        for campo in ("Hora_Inicio", "Hora_Fin"):
            _, causa = norm.normalizar_hora(fila.datos.get(campo))
            if causa:
                _agregar(
                    cola,
                    fila,
                    clave,
                    Motivo.DATO_INCOMPLETO,
                    Gravedad.A_CONFIRMAR,
                    str(fila.datos.get(campo) or ""),
                    causa,
                )
        hora_inicio, _ = norm.normalizar_hora(fila.datos.get("Hora_Inicio"))
        hora_fin, _ = norm.normalizar_hora(fila.datos.get("Hora_Fin"))

        km, motivo_km = norm.normalizar_decimal_argentino(fila.datos.get("Km_Recorridos"))
        if motivo_km:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DATO_INCOMPLETO,
                Gravedad.A_CONFIRMAR,
                str(fila.datos.get("Km_Recorridos") or ""),
                motivo_km,
            )

        bultos_texto = str(fila.datos.get("Bultos_Estimados") or "").strip()
        bultos, motivo_bultos = norm.normalizar_bultos(fila.datos.get("Bultos_Estimados"))
        if motivo_bultos:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.TEXTO_AMBIGUO,
                Gravedad.A_CONFIRMAR,
                bultos_texto,
                f"{motivo_bultos} Se dejó `bultos_estimados` en NULL y el texto original se "
                "conserva para que alguien lo lea.",
            )

        monto, motivo_monto = norm.normalizar_monto(fila.datos.get("Monto_Cobrado"))
        if motivo_monto:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.DATO_INCOMPLETO,
                Gravedad.BLOQUEANTE,
                str(fila.datos.get("Monto_Cobrado") or ""),
                motivo_monto,
            )
        elif monto and monto.es_extranjera:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.MONEDA_EXTRANJERA,
                Gravedad.BLOQUEANTE,
                str(fila.datos.get("Monto_Cobrado") or ""),
                f"El monto está en dólares ({monto.valor} USD). No se convirtió a pesos: falta que "
                "el cliente confirme el tipo de cambio y la fecha.",
            )

        cobro, motivos_cobro = norm.descomponer_estado_cobro(
            fila.datos.get("Estado_Cobro"), monto.valor if monto else None
        )
        for motivo_cobro in motivos_cobro:
            _agregar(
                cola,
                fila,
                clave,
                Motivo.TEXTO_AMBIGUO,
                Gravedad.A_CONFIRMAR,
                str(fila.datos.get("Estado_Cobro") or ""),
                motivo_cobro,
            )

        chofer = str(fila.datos.get("Chofer_Asignado") or "").strip()
        cliente = str(fila.datos.get("Cliente") or "").strip()
        viajes.append(
            Viaje(
                codigo=clave,
                fecha=fecha.valor,
                fecha_formato_origen=fecha.formato_origen,
                chofer_nombre=chofer,
                chofer_nombre_key=norm.normalizar_texto(chofer),
                cliente_nombre=cliente,
                cliente_nombre_key=norm.normalizar_texto(cliente),
                origen=str(fila.datos.get("Origen_Direccion") or "").strip(),
                destino=str(fila.datos.get("Destino_Direccion") or "").strip(),
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                km_recorridos=km,
                bultos_estimados=bultos.cantidad,
                bultos_texto_original=bultos_texto,
                monto_cobrado=monto.valor if monto else None,
                moneda_monto=monto.moneda if monto else norm.MONEDA_PESO,
                pago_medio=cobro.medio,
                pago_estado=cobro.estado,
                pago_saldo=cobro.saldo,
                fila_origen=fila.numero,
                hoja_origen=fila.hoja,
            )
        )
        vistos[clave] = fila.numero

    return viajes, cola


def cruzar_viajes_con_choferes(
    viajes: list[Viaje], moviles: list[Movil]
) -> tuple[dict[str, str], list[RevisionHumana]]:
    """Cruza cada viaje con su móvil por nombre de chofer normalizado.

    Devuelve `(mapa codigo_viaje -> codigo_movil, casos_para_revision)`. Los nombres se comparan
    con la clave sin acentos ni mayúsculas, así que `"MARCELO RODRIGUEZ"` y `"Marcelo Rodriguez"`
    caen en el mismo chofer. La tabla `choferes` todavía no existe: el cruce es en memoria contra
    los nombres del propio archivo, y sirve para saber si más adelante va a poder resolverse.
    """
    por_nombre: dict[str, list[Movil]] = {}
    for movil in moviles:
        por_nombre.setdefault(movil.nombre_chofer_key, []).append(movil)

    mapa: dict[str, str] = {}
    casos: list[RevisionHumana] = []
    for viaje in viajes:
        candidatos = por_nombre.get(viaje.chofer_nombre_key)
        if not candidatos:
            casos.append(
                RevisionHumana(
                    hoja=viaje.hoja_origen,
                    fila=viaje.fila_origen,
                    clave=viaje.codigo,
                    motivo=Motivo.SIN_MAPEO_EN_MODELO,
                    gravedad=Gravedad.A_CONFIRMAR,
                    valor_original=viaje.chofer_nombre,
                    detalle=f"El viaje cita al chofer «{viaje.chofer_nombre}» y no está en "
                    "`Choferes_y_Moviles`. Sin la tabla `choferes` no se puede resolver la "
                    "referencia.",
                )
            )
            continue
        if len(candidatos) > 1:
            codigos = ", ".join(movil.codigo for movil in candidatos)
            casos.append(
                RevisionHumana(
                    hoja=viaje.hoja_origen,
                    fila=viaje.fila_origen,
                    clave=viaje.codigo,
                    motivo=Motivo.DUPLICADO,
                    gravedad=Gravedad.BLOQUEANTE,
                    valor_original=viaje.chofer_nombre,
                    detalle=f"«{viaje.chofer_nombre}» corresponde a más de un móvil "
                    f"({codigos}) y no se puede decidir a cuál pertenece el viaje.",
                )
            )
            continue
        mapa[viaje.codigo] = candidatos[0].codigo
    return mapa, casos


def aplicar_cruce(viajes: list[Viaje], mapa: dict[str, str]) -> None:
    """Deja el código de móvil en cada viaje que se pudo cruzar."""
    for viaje in viajes:
        viaje.movil_codigo = mapa.get(viaje.codigo)
