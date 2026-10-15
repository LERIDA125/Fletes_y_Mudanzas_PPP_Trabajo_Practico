"""Carga de los datos migrados. **Único módulo que escribe en la base de datos.**

La escritura pasa siempre por `ClienteRepo` de H1 (AGENTS.md §2: el repositorio es el único punto de
acceso a PostgreSQL). Este módulo no escribe SQL, no abre una sesión propia y no redefine la entidad
`Cliente`: arma el dominio con la API que H1 dejó y se lo pasa al repositorio.

Por qué importa: si la migración hiciera `INSERT` a mano, esquivaría el `UNIQUE` de
`razon_social_key`, la validación del dominio y el manejo de errores de H1, y la idempotencia
(FR-005) quedaría en manos de un `SELECT` improvisado.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.cliente import Cliente
from app.domain.errores import RazonSocialDuplicada, ReglaNegocioError
from app.infrastructure.repositories.cliente_repo import ClienteRepo
from scripts.migracion.revision import Gravedad, Motivo, RevisionHumana
from scripts.migracion.transformacion import ClienteMigrable


@dataclass
class ResultadoCarga:
    """Qué pasó con cada cliente, para que el reporte pueda decirlo sin volver a mirar la base."""

    agregados: list[Cliente] = field(default_factory=list)
    ya_existentes: list[str] = field(default_factory=list)
    omitidos: list[str] = field(default_factory=list)
    casos: list[RevisionHumana] = field(default_factory=list)

    @property
    def total_procesados(self) -> int:
        return len(self.agregados) + len(self.ya_existentes) + len(self.omitidos)

    @property
    def escribio(self) -> bool:
        """False cuando la corrida no llegó a insertar nada: no se abrió ni una sesión."""
        return bool(self.agregados)


def cliente_creable(migrable: ClienteMigrable) -> Cliente:
    """Arma la entidad de dominio con los cuatro campos que H1 define.

    `tiene_cuenta_corriente` va **siempre** en `False`: `Historial_Pagos` es una nota en palabras y
    traducirla a un booleano sería inventar la política de cuenta corriente (DP-06, AGENTS.md §6).
    """
    return Cliente.crear(
        razon_social=migrable.nombre,
        telefono=migrable.telefono or "",
        direccion_habitual=migrable.direccion,
        tiene_cuenta_corriente=False,
    )


def cargar_clientes(
    clientes: list[ClienteMigrable], repo: ClienteRepo, simular: bool = False
) -> ResultadoCarga:
    """Carga los clientes usando el repositorio de H1, sin duplicar en una segunda corrida.

    La idempotencia se apoya en `existe_razon_social`, que ya compara por `razon_social_key`
    (minúsculas, sin acentos, sin espacios sobrantes — DD-2). Un cliente que ya está en la base no
    se vuelve a insertar: se cuenta como "ya existente".

    `simular=True` no escribe nada y solo informa qué se agregaría. Es lo que permite ver el plan de
    carga contra una base real sin tocarlo.
    """
    resultado = ResultadoCarga()

    for migrable in clientes:
        if migrable.telefono is None:
            # `Cliente` exige entre 7 y 20 dígitos (FR-005). Sin teléfono la fila no se puede
            # cargar: se omite y se explica. Inventar un teléfono para que entre sería peor que
            # dejar la fila para que la complete una persona.
            motivo = "el teléfono no se pudo normalizar"
            resultado.omitidos.append(migrable.nombre)
            resultado.casos.append(
                RevisionHumana(
                    hoja=migrable.hoja_origen,
                    fila=migrable.fila_origen,
                    clave=migrable.codigo_origen,
                    motivo=Motivo.DATO_INCOMPLETO,
                    gravedad=Gravedad.BLOQUEANTE,
                    valor_original=migrable.nombre,
                    detalle=f"El cliente se omitió porque {motivo}: el `Cliente` de H1 exige un "
                    "teléfono de entre 7 y 20 dígitos y no hay cuál usar.",
                )
            )
            continue

        try:
            # El dominio valida en `__post_init__`: si la razón social, el teléfono o la dirección
            # no dan la talla, `crear` levanta `ReglaNegocioError` acá. No hace falta un método de
            # validación aparte, y agregarle uno a `Cliente` sería tocar una entidad de H1.
            cliente = cliente_creable(migrable)
        except ReglaNegocioError as error:
            resultado.omitidos.append(migrable.nombre)
            resultado.casos.append(
                RevisionHumana(
                    hoja=migrable.hoja_origen,
                    fila=migrable.fila_origen,
                    clave=migrable.codigo_origen,
                    motivo=Motivo.DATO_INCOMPLETO,
                    gravedad=Gravedad.BLOQUEANTE,
                    valor_original=migrable.nombre,
                    detalle=f"El cliente se omitió porque el dominio lo rechazó: {error}",
                )
            )
            continue

        if repo.existe_razon_social(cliente.razon_social_key):
            resultado.ya_existentes.append(migrable.nombre)
            continue

        if simular:
            resultado.agregados.append(cliente)
            continue

        try:
            # Ojo con el orden: primero se crea y recién después se agrega al resultado. Si se
            # escribiera `agregados.append(repo.crear(...))`, una excepción dejaría la lista sin
            # ese elemento y el `except` no tendría qué deshacer.
            creado = repo.crear(cliente)
        except RazonSocialDuplicada:
            # `existe_razon_social` dijo que no estaba, pero el `UNIQUE` de la base lo rechazó:
            # otra corrida del script (o una carga manual) lo insertsó entre medio. Se lo trata
            # como ya existente en vez de cortar, y se avisa para que la persona lo verifique.
            resultado.ya_existentes.append(migrable.nombre)
            resultado.casos.append(
                RevisionHumana(
                    hoja=migrable.hoja_origen,
                    fila=migrable.fila_origen,
                    clave=migrable.codigo_origen,
                    motivo=Motivo.DUPLICADO,
                    gravedad=Gravedad.A_CONFIRMAR,
                    valor_original=migrable.nombre,
                    detalle="La razón social ya estaba en la base cuando se intentó insertar, "
                    "aunque el chequeo previo decía que no. Se trata como el mismo "
                    "cliente; conviene confirmar que sea la misma persona y no dos "
                    "homónimas.",
                )
            )
            continue

        resultado.agregados.append(creado)

    return resultado
