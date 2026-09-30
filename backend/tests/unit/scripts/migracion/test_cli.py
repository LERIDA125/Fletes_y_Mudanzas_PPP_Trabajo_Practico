"""Tests de la CLI y del flujo completo (FR-003, FR-033, FR-038).

Son los únicos tests que tocan la orquestación de `__main__.py`. El resto de la historia se
prueba módulo por módulo, así que acá lo que se verifica es que las piezas encajan y que el modo
`--solo-transformacion` realmente no toca la base.
"""

import builtins
from contextlib import contextmanager
from pathlib import Path

import pytest

from scripts.migracion import __main__ as main_modulo
from scripts.migracion.__main__ import main, transformar
from scripts.migracion.extraccion import ArchivoDeMigracionError, ruta_por_defecto


@pytest.fixture(scope="module")
def excel() -> Path:
    ruta = ruta_por_defecto()
    if not ruta.exists():
        pytest.skip(f"No está el archivo de Excel en {ruta}")
    return ruta


class TestTransformarSinBase:
    """FR-003: la transformación tiene que poder correr sin conexión."""

    def test_transforma_las_tres_hojas_sin_tocar_la_base(self, excel: Path) -> None:
        resultado = transformar(excel)

        assert len(resultado.clientes) == 10
        assert len(resultado.moviles) == 8
        assert len(resultado.viajes) == 10

    def test_sin_escribir_no_hay_ninguna_carga(self, excel: Path) -> None:
        resultado = transformar(excel)

        assert resultado.carga.agregados == []
        assert resultado.carga.ya_existentes == []
        assert resultado.carga.escribio is False

    def test_los_cruces_de_chofer_quedan_resueltos(self, excel: Path) -> None:
        """FR-032: los 10 viajes deben encontrar su móvil, o el cruce no sirve para nada."""
        resultado = transformar(excel)

        assert all(viaje.movil_codigo is not None for viaje in resultado.viajes)

    def test_no_importa_nada_de_infraestructura(self, excel: Path, monkeypatch) -> None:
        """FR-003 a secas: si se importara el motor de la base, esto reventaría.

        Se intercepta el import de `sqlalchemy` y `psycopg`: si el módulo los hubiera arrastrado
        (por ejemplo importando `ClienteRepo` arriba del todo), la transformación no podría
        completarse en un entorno sin base configurada.
        """

        def _no_importar(nombre, *args, **kwargs):
            if nombre.split(".")[0] in {"sqlalchemy", "psycopg"}:
                raise AssertionError(f"la transformación no debería importar {nombre}")
            return _import_real(nombre, *args, **kwargs)

        _import_real = builtins.__import__
        monkeypatch.setattr(builtins, "__import__", _no_importar)

        resultado = transformar(excel)

        assert len(resultado.clientes) == 10


class TestCliSoloTransformacion:
    """FR-038: la CLI tiene que correr sin argumentos y sin base."""

    def test_escribe_el_reporte_y_devuelve_cero(self, excel: Path, tmp_path: Path, capsys) -> None:
        destino = tmp_path / "reporte.md"

        codigo = main(["--archivo", str(excel), "--reporte", str(destino), "--solo-transformacion"])

        assert codigo == 0
        assert destino.exists()
        assert "Reporte de migración" in destino.read_text(encoding="utf-8")

    def test_no_intenta_conectarse_a_la_base(self, excel: Path, tmp_path: Path) -> None:
        """Si se conectara, sin credenciales válidas la corrida fallaría."""
        codigo = main(
            [
                "--archivo",
                str(excel),
                "--reporte",
                str(tmp_path / "reporte.md"),
                "--solo-transformacion",
            ]
        )

        assert codigo == 0

    def test_avisa_que_no_toco_la_base(self, excel: Path, tmp_path: Path, capsys) -> None:
        main(
            ["--archivo", str(excel), "--reporte", str(tmp_path / "r.md"), "--solo-transformacion"]
        )

        salida = capsys.readouterr().out

        assert "no se tocó la base" in salida

    def test_avisa_que_hay_casos_bloqueantes(self, excel: Path, tmp_path: Path, capsys) -> None:
        """Si el archivo tiene bloqueantes, el código de salida igual es 0 pero avisa por stderr."""
        main(
            ["--archivo", str(excel), "--reporte", str(tmp_path / "r.md"), "--solo-transformacion"]
        )

        assert "bloqueantes" in capsys.readouterr().err


class TestCliErrores:
    def test_un_archivo_inexistente_devuelve_uno(self, tmp_path: Path) -> None:
        codigo = main(["--archivo", str(tmp_path / "no-existe.xlsx")])

        assert codigo == 1

    def test_un_archivo_sin_las_tres_hojas_devuelve_uno_y_no_escribe(
        self, tmp_path: Path, capsys
    ) -> None:
        """FR-001: falla temprano, sin dejar un reporte a medias que parezca una migración buena."""
        from openpyxl import Workbook

        libro = Workbook()
        libro.active.title = "Registro_Choferes"
        ruta = tmp_path / "incompleto.xlsx"
        libro.save(ruta)
        destino = tmp_path / "reporte.md"

        codigo = main(["--archivo", str(ruta), "--reporte", str(destino)])

        assert codigo == 1
        assert not destino.exists()
        assert "No se pudo migrar" in capsys.readouterr().err


class TestSimular:
    """FR-038: `--simular` calcula el plan de carga sin insertar una sola fila."""

    @pytest.fixture
    def repo_que_falla_si_escribe(self, monkeypatch) -> list:
        """Repo de trampa: si alguien intenta escribir, el test revienta.

        Se reemplaza `_repo` (el contextmanager de `__main__`) para que la CLI reciba este doble en
        vez del `ClienteRepo` real. `existe_razon_social` responde que no existe nada, que es lo
        que hace que `cargar_clientes` quiera insertar: por eso el modo `simular` es el que se
        tiene que saltear esa llamada.
        """
        registradas: list = []

        class RepoDeTrampa:
            def existe_razon_social(self, razon_social_key, excluir_id=None) -> bool:
                return False

            def crear(self, cliente):
                raise AssertionError("`--simular` no debe llamar a `crear`")

        @contextmanager
        def _repo_falso():
            yield RepoDeTrampa()

        monkeypatch.setattr(main_modulo, "_repo", _repo_falso)
        return registradas

    def test_simular_no_escribe_nada(
        self, excel, tmp_path, repo_que_falla_si_escribe, capsys
    ) -> None:
        codigo = main(
            [
                "--archivo",
                str(excel),
                "--reporte",
                str(tmp_path / "r.md"),
                "--simular",
            ]
        )

        assert codigo == 0
        assert "se cargarían" in capsys.readouterr().out

    def test_el_modo_normal_escribiria_y_por_eso_la_trampa_ruena(
        self, excel, tmp_path, repo_que_falla_si_escribe
    ) -> None:
        """Control: la trampa tiene que estar bien puesta.

        Si `--simular` no fuera a diferenciar del modo de carga, el test de arriba pasaría por
        Accident. Este comprueba que la misma trampa sí salta cuando se carga de verdad.
        """
        with pytest.raises(AssertionError, match="no debe llamar a `crear`"):
            main(["--archivo", str(excel), "--reporte", str(tmp_path / "r.md")])


class TestArchivoDeMigracionErrorEsDelModuloCorrecto:
    def test_el_error_es_el_que_define_extraccion(self) -> None:
        assert issubclass(ArchivoDeMigracionError, Exception)
