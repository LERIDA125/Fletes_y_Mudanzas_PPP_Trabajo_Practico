"""Tests del reporte (FR-034 a FR-036)."""

from datetime import date
from decimal import Decimal

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
    datos_dict = {
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
    datos_dict.update(extra)
    return Movil(**datos_dict)


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
    def test_el_reporte_tiene_las_secciones_y_metadatos_requeridos(self) -> None:
        texto = generar_markdown(datos())
        for seccion in [
            "# Reporte de migración de datos históricos",
            "## Resumen",
            "## Transformaciones aplicadas",
            "## Casos para revisión humana",
            "## Gaps de mapeo",
        ]:
            assert seccion in texto

        assert "raw-data/datos.xlsx" in texto
        assert "no están confirmados por el cliente" in texto
        assert "Medios de pago (PROPUESTOS, no confirmados)" in texto


class TestTransformacionesAplicadas:
    def test_cada_transformacion_y_hoja_esta_descrita(self) -> None:
        texto = generar_markdown(datos())
        columnas = [
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
        ]
        for columna in columnas:
            assert columna in texto

        assert "Choferes_y_Moviles" in texto
        assert "Clientes_Cotizaciones" in texto
        assert "Registro_Viajes" in texto


class TestRevisionHumana:
    def test_secciones_y_formato_de_revision_humana(self) -> None:
        texto = generar_markdown(datos(casos=[CASO, BLOQUEANTE]))
        assert "## Bloqueantes (1)" in texto
        assert "## Para confirmar (1)" in texto
        assert "2 (1 bloqueantes, 1 para confirmar)" in texto

        texto_caso = generar_markdown(datos(casos=[CASO]))
        assert "Registro_Viajes" in texto_caso
        assert "VJ-2005" in texto_caso
        assert "Anotado en la libreta" in texto_caso

        texto_vacio = generar_markdown(datos(casos=[]))
        assert "No quedó ningún caso para revisar" in texto_vacio
        assert "## Bloqueantes" not in texto_vacio

        texto_obs = generar_markdown(datos())
        assert "En taller hasta el martes" in texto_obs
        assert "Archivadores pesados" in texto_obs


class TestGapsDeMapeo:
    def test_columnas_sin_destino_nombradas_en_reporte(self) -> None:
        texto = generar_markdown(datos())
        for columna in [
            "`ID_Cliente`",
            "`Localidad_Barrio`",
            "`Condicion_IVA`",
            "`Historial_Pagos`",
        ]:
            assert columna in texto
        assert "No se agregó ninguna columna a las entidades" in texto
        assert "requiere acordarlo con quien implementó H1" in texto


class TestResumen:
    def test_resumen_y_listado_de_omitidos(self) -> None:
        carga = ResultadoCarga(agregados=[cliente("Uno")], ya_existentes=["Dos"], omitidos=["Tres"])
        texto = generar_markdown(datos(carga=carga))
        assert "cargados: **1**" in texto
        assert "ya existentes: **1**" in texto
        assert "omitidos: **1**" in texto

        texto_base = generar_markdown(datos())
        assert "tabla `choferes` + `vehiculos`" in texto_base
        assert "pendiente: la tabla no existe" in texto_base
        assert "tabla `servicios`" in texto_base
        assert "tabla `pagos`" in texto_base

        carga_omitidos = ResultadoCarga(omitidos=["Juan Carlos Gomez"])
        texto_omit = generar_markdown(datos(carga=carga_omitidos))
        assert "Clientes que no se pudieron cargar" in texto_omit
        assert "Juan Carlos Gomez" in texto_omit
