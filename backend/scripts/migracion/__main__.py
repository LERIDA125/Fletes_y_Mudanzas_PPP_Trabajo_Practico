"""Punto de entrada de la migración: `python -m scripts.migracion`.

Orquesta el flujo completo (lectura → transformación → carga → reporte) y nada más. Toda la lógica
está en los módulos que llama; acá solo se resuelve la línea de comandos y el manejo de errores.

Dos formas de correrlo sin base de datos:

- `--solo-transformacion`: ni siquiera intenta conectarse. Es la que puede correr en CI.
- `--simular`: se conecta y lee, pero no inserta. Sirve para ver qué se agregaría contra una base
  real.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from scripts.migracion import carga as mod_carga
from scripts.migracion import extraccion, reporte, transformacion
from scripts.migracion.revision import ColaDeRevision
from scripts.migracion.transformacion import ClienteMigrable, Movil, Viaje

RAIZ_BACKEND = Path(__file__).resolve().parents[2]
RUTA_REPORTE_POR_DEFECTO = RAIZ_BACKEND / "data" / "reporte_migracion.md"


@dataclass
class Resultado:
    """Lo que devuelve la corrida, para que la CLI imprima el resumen y el reporte use lo mismo."""

    clientes: list[ClienteMigrable]
    moviles: list[Movil]
    viajes: list[Viaje]
    carga: mod_carga.ResultadoCarga
    cola: ColaDeRevision


def transformar(ruta: Path) -> Resultado:
    """Lee el Excel y normaliza las tres hojas. No toca la base de datos.

    Se puede correr sin conexión: por eso la transformación está separada de la carga.
    """
    extraccion.verificar_hojas(ruta)

    moviles, cola_moviles = transformacion.transformar_moviles(extraccion.leer_choferes(ruta))
    clientes, cola_clientes = transformacion.transformar_clientes(extraccion.leer_clientes(ruta))
    viajes, cola_viajes = transformacion.transformar_viajes(extraccion.leer_viajes(ruta))

    mapa, casos_cruce = transformacion.cruzar_viajes_con_choferes(viajes, moviles)
    transformacion.aplicar_cruce(viajes, mapa)

    cola = ColaDeRevision()
    cola.extender(cola_moviles)
    cola.extender(cola_clientes)
    cola.extender(cola_viajes)
    cola.agregar_varios(casos_cruce)

    return Resultado(
        clientes=clientes,
        moviles=moviles,
        viajes=viajes,
        carga=mod_carga.ResultadoCarga(),
        cola=cola,
    )


@contextmanager
def _repo() -> Iterator:
    """Arma el `ClienteRepo` real y cierra la sesión al salir.

    La sesión se abre adentro del `with` a propósito: si un `INSERT` dejara la transacción a medio
    hacer, salirse sin cerrar la sesión devolvería al pool una conexión en estado sucio y la
    corrida siguiente heredaría el problema.

    El import está adentro del contextmanager para que `--solo-transformacion` no necesite
    configuración de base de datos ni psycopg.
    """
    from app.infrastructure.db.session import SessionLocal
    from app.infrastructure.repositories.cliente_repo import ClienteRepo

    with SessionLocal() as sesion:
        yield ClienteRepo(sesion)


def correr(
    ruta: Path,
    ruta_reporte: Path,
    solo_transformacion: bool = False,
    simular: bool = False,
) -> Resultado:
    """Ejecuta la migración completa y escribe el reporte."""
    resultado = transformar(ruta)

    if not solo_transformacion:
        with _repo() as repo:
            resultado.carga = mod_carga.cargar_clientes(resultado.clientes, repo, simular=simular)
        resultado.cola.agregar_varios(resultado.carga.casos)

    datos = reporte.DatosReporte(
        clientes=resultado.clientes,
        moviles=resultado.moviles,
        viajes=resultado.viajes,
        carga=resultado.carga,
        casos=resultado.cola.casos,
        archivo_origen=str(ruta),
        generado_en=date.today(),
    )
    reporte.escribir_reporte(datos, ruta_reporte)

    return resultado


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.migracion",
        description=(
            "Migra los datos históricos del Excel al modelo relacional. Es idempotente: se puede "
            "volver a correr sin duplicar clientes."
        ),
    )
    parser.add_argument(
        "--archivo",
        type=Path,
        default=None,
        help="Ruta del archivo de Excel. Por defecto, el de raw-data/.",
    )
    parser.add_argument(
        "--reporte",
        type=Path,
        default=RUTA_REPORTE_POR_DEFECTO,
        help="Dónde escribir el reporte Markdown.",
    )
    parser.add_argument(
        "--solo-transformacion",
        action="store_true",
        help="Normaliza y escribe el reporte sin conectarse a la base de datos.",
    )
    parser.add_argument(
        "--simular",
        action="store_true",
        help="Se conecta y lee, pero no inserta nada. Informa qué se cargaría.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    argumentos = _parser().parse_args(argv)
    ruta = argumentos.archivo or extraccion.ruta_por_defecto()

    if not ruta.exists():
        print(f"No se encontró el archivo de Excel en {ruta}", file=sys.stderr)
        return 1

    try:
        resultado = correr(
            ruta,
            argumentos.reporte,
            solo_transformacion=argumentos.solo_transformacion,
            simular=argumentos.simular,
        )
    except extraccion.ArchivoDeMigracionError as error:
        # Falla temprano y sin escribir nada: no se migra la mitad del archivo (FR-001).
        print(f"No se pudo migrar: {error}", file=sys.stderr)
        return 1

    carga = resultado.carga

    if argumentos.solo_transformacion:
        print(f"Clientes: {len(carga.agregados)} (no se tocó la base: modo solo-transformación).")
    else:
        verbos = "se cargarían" if argumentos.simular else "se cargaron"
        print(
            f"Clientes: {len(carga.agregados)} {verbos}, "
            f"{len(carga.ya_existentes)} ya existentes, {len(carga.omitidos)} omitidos."
        )
    print(f"Móviles: {len(resultado.moviles)} transformados (pendiente: la tabla no existe).")
    print(f"Viajes: {len(resultado.viajes)} transformados (pendiente: la tabla no existe).")
    print(f"Casos para revisión humana: {len(resultado.cola)}.")
    print(f"Reporte: {argumentos.reporte}")

    if resultado.cola.hay_bloqueantes:
        print(
            f"\nOjo: hay casos bloqueantes sin resolver. Mirá la sección correspondiente de "
            f"{argumentos.reporte} antes de tomar la base como fuente de verdad.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
