"""Tests del reporte (FR-034 a FR-036).

El reporte es el entregable que le dice a una persona qué mirar. Estos tests verifican que tenga las
secciones que la spec exige y que cada caso quede con su hoja, su fila y su valor original, que es
lo que permite rastrear el dato hasta el Excel.
"""

from datetime import date
from decimal import Decimal

import pytest

from scripts.migracion.carga import ResultadoCarga
from scripts.migracion.reporte import DatosReporte, generar_markdown
from scripts.migracion.revision import Gravedad, Motivo, RevisionHumana
from scripts.migracion.transformacion import ClienteMigrable, Movil, Viaje

CASO = RevisionHumana(
    hoja="Registro_Viajes",
    fila=6,
    clave="VJ-2005",
    motivo=Motivo.TEXTO_AMBIGUO,
    gravedad=Gravedad.A_CONFIRMAR,
    valor_original="Anotado en la libreta",
    detalle="No dice medio de pago ni si el cobro está completo.",
)

BLOQUEANTE = RevisionHumana(
    hoja="Choferes_y_Moviles",
    fila=8,
    clave="MOV-05",
    motivo=Motivo.MONEDA_EXTRANJERA,
    gravedad=Gravedad.BLOQUEANTE,
    valor_original="U$S 15",
    detalle="El valor está en dólares. No se convirtió a pesos.",
)


def movil(**extra) -> Movil:
    datos = {
        "codigo": "MOV-02",
        "nombre_chofer": "El Ruso",
        "nombre_chofer_key": "el ruso",
        "telefono": "1533229988",
        "tipo_vehiculo": "Camioneta Mediana",
        "capacidad_kg": Decimal("800"),
        "tarifa_hora_base": Decimal("11000"),
        "tarifa_km_excedente": Decimal("380"),
        "moneda_tarifa": "ARS",
        "estado": "inactivo",
        "observaciones": ["En taller hasta el martes"],
        "filas_de_origen": [4],
    }
    datos.update(extra)
    return Movil(**datos)


def cliente(nombre: str = "Uno") -> ClienteMigrable:
    return ClienteMigrable(
        nombre=nombre,
        nombre_key=nombre.lower(),
        telefono="1122334455",
        direccion="Av. Cabildo 2140",
        direccion_es_estructurada=True,
        codigo_origen="CLI-101",
        localidad_barrio="Belgrano, CABA",
        condicion_iva="Responsable Inscripto",
        historial_pagos="Paga a 30 días",
        fila_origen=2,
        hoja_origen="Clientes_Cotizaciones",
    )


def viaje(codigo: str = "VJ-2001") -> Viaje:
    return Viaje(
        codigo=codigo,
        fecha=date(2026, 5, 15),
        fecha_formato_origen="dd/mm/aaaa",
        chofer_nombre="Marcelo Rodriguez",
        chofer_nombre_key="marcelo rodriguez",
        cliente_nombre="Muebles Belgrano S.R.L.",
        cliente_nombre_key="muebles belgrano s.r.l.",
        origen="Av. Cabildo 2140",
        destino="San Martin 1200",
        hora_inicio=None,
        hora_fin=None,
        km_recorridos=Decimal("35.5"),
        bultos_estimados=None,
        bultos_texto_original="Archivadores pesados",
        monto_cobrado=Decimal("58500"),
        moneda_monto="ARS",
        pago_medio="Transferencia bancaria",
        pago_estado="cobrado",
        pago_saldo=Decimal("0"),
        fila_origen=2,
        hoja_origen="Registro_Viajes",
    )


def datos(casos=None, carga=None, clientes=None, moviles=None, viajes=None) -> DatosReporte:
    return DatosReporte(
        clientes=clientes if clientes is not None else [cliente()],
        moviles=moviles if moviles is not None else [movil()],
        viajes=viajes if viajes is not None else [viaje()],
        carga=carga if carga is not None else ResultadoCarga(),
        casos=casos if casos is not None else [],
        archivo_origen="raw-data/datos.xlsx",
        generado_en=date(2026, 9, 30),
    )


class TestSecciones:
    @pytest.mark.parametrize(
        "seccion",
        [
            "# Reporte de migración de datos históricos",
            "## Resumen",
            "## Transformaciones aplicadas",
            "## Casos para revisión humana",
            "## Gaps de mapeo",
        ],
    )
    def test_el_reporte_tiene_las_secciones_que_pide_la_spec(self, seccion: str) -> None:
        """FR-034: las secciones tienen que estar separadas, no mezcladas en un bloque de texto."""
        assert seccion in generar_markdown(datos())

    def test_el_reporte_nombra_el_archivo_de_origen(self) -> None:
        assert "raw-data/datos.xlsx" in generar_markdown(datos())

    def test_el_reporte_avisa_los_catologos_provisionales(self) -> None:
        texto = generar_markdown(datos())

        assert "no están confirmados por el cliente" in texto
        assert "Medios de pago (PROPUESTOS, no confirmados)" in texto


class TestTransformacionesAplicadas:
    @pytest.mark.parametrize(
        "columna",
        [
            "`Cod_Movil`",
            "`Telefono_Contacto`",
            "`Tipo_Vehiculo`",
            "`Capacidad_Carga`",
            "`Tarifa_Hora_Base`, `Tarifa_Km_Excedente`",
            "`Estado_Actual`",
            "`ID_Cliente`",
            "`Condicion_IVA`",
            "`Historial_Pagos`",
            "`Nro_Viaje`",
            "`Fecha_Servicio`",
            "`Hora_Inicio`, `Hora_Fin`",
            "`Km_Recorridos`",
            "`Bultos_Estimados`",
            "`Monto_Cobrado`",
            "`Estado_Cobro`",
        ],
    )
    def test_cada_transformacion_de_la_planilla_esta_descrita(self, columna: str) -> None:
        texto = generar_markdown(datos())

        assert columna in texto

    def test_cada_fila_dice_de_que_hoja_va(self) -> None:
        texto = generar_markdown(datos())

        assert "Choferes_y_Moviles" in texto
        assert "Clientes_Cotizaciones" in texto
        assert "Registro_Viajes" in texto


class TestRevisionHumana:
    def test_los_bloqueantes_y_los_de_confirmacion_estan_en_secciones_distintas(self) -> None:
        """FR-036: hay que poder saber de entrada qué frena la migración."""
        texto = generar_markdown(datos(casos=[CASO, BLOQUEANTE]))

        assert "## Bloqueantes (1)" in texto
        assert "## Para confirmar (1)" in texto

    def test_cada_caso_cita_la_hoja_la_fila_y_el_valor_original(self) -> None:
        """FR-035: sin la fila original el caso no se puede buscar en el Excel."""
        texto = generar_markdown(datos(casos=[CASO]))

        assert "Registro_Viajes" in texto
        assert "VJ-2005" in texto
        assert "Anotado en la libreta" in texto

    def test_el_cuenta_de_casos_aparece_en_el_encabezado(self) -> None:
        texto = generar_markdown(datos(casos=[CASO, BLOQUEANTE]))

        assert "2 (1 bloqueantes, 1 para confirmar)" in texto

    def test_sin_casos_el_reporte_lo_dice_y_no_inventa_una_tabla(self) -> None:
        texto = generar_markdown(datos(casos=[]))

        assert "No quedó ningún caso para revisar" in texto
        assert "## Bloqueantes" not in texto

    def test_los_textos_preservados_aparecen_con_su_original(self) -> None:
        """SC-005: el texto libre tiene que poder leerse, no solo haberse mapeado."""
        texto = generar_markdown(datos())

        assert "En taller hasta el martes" in texto
        assert "Archivadores pesados" in texto


class TestGapsDeMapeo:
    @pytest.mark.parametrize(
        "columna", ["`ID_Cliente`", "`Localidad_Barrio`", "`Condicion_IVA`", "`Historial_Pagos`"]
    )
    def test_las_cuatro_columnas_sin_destino_estan_nombradas(self, columna: str) -> None:
        """FR-020 / SC-006: el gap se reporta, no se resuelve agregando una columna."""
        assert columna in generar_markdown(datos())

    def test_el_reporte_dice_que_no_se_agrego_ninguna_columna(self) -> None:
        texto = generar_markdown(datos())

        assert "No se agregó ninguna columna a las entidades" in texto
        assert "requiere acordarlo con quien implementó H1" in texto


class TestResumen:
    def test_dice_cuantos_clientes_se_cargaron_y_cuantos_ya_existian(self) -> None:
        carga = ResultadoCarga(agregados=[cliente("Uno")], ya_existentes=["Dos"], omitidos=["Tres"])
        texto = generar_markdown(datos(carga=carga))

        assert "cargados: **1**" in texto
        assert "ya existentes: **1**" in texto
        assert "omitidos: **1**" in texto

    def test_dice_que_las_tablas_que_faltan_no_se_escribieron(self) -> None:
        """DP-09: el reporte tiene que dejar claro el alcance de la carga."""
        texto = generar_markdown(datos())

        assert "tabla `choferes` + `vehiculos`" in texto
        assert "pendiente: la tabla no existe" in texto
        assert "tabla `servicios`" in texto
        assert "tabla `pagos`" in texto

    def test_los_omitidos_se_listan_por_nombre(self) -> None:
        """FR-033: lo que no se escribió queda nombrado en el reporte, no solo contado."""
        carga = ResultadoCarga(omitidos=["Juan Carlos Gomez"])
        texto = generar_markdown(datos(carga=carga))

        assert "Clientes que no se pudieron cargar" in texto
        assert "Juan Carlos Gomez" in texto
