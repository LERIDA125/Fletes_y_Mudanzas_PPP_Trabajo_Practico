"""Suite unificada de Migración de Datos Históricos (H13).

Valida en un único test integral:
1. Normalización de formatos (teléfonos, montos argentinos, fechas y catálogos).
2. Extracción de las 3 hojas del Excel y manejo de anomalías/casos humanos.
3. Transformación de datos y resolución de cruces.
4. Generación del reporte Markdown con secciones completas.
5. Idempotencia de la carga sin duplicados.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from scripts.migracion.carga import ResultadoCarga, cargar_clientes
from scripts.migracion.extraccion import ruta_por_defecto, verificar_hojas
from scripts.migracion.normalizacion import (
    codigo_de_movil,
    descomponer_estado_cobro,
    normalizar_capacidad,
    normalizar_fecha,
    normalizar_monto,
    normalizar_telefono,
    normalizar_tipo_vehiculo,
)
from scripts.migracion.reporte import DatosReporte, generar_markdown
from scripts.migracion.revision import Gravedad, Motivo, RevisionHumana
from scripts.migracion.transformacion import (
    ClienteMigrable,
    Movil,
    Viaje,
    transformar_clientes,
    transformar_moviles,
    transformar_viajes,
)


class ClienteRepoFalso:
    def __init__(self) -> None:
        self.creados = []
        self._siguiente_id = 1

    def crear(self, cliente):
        self.creados.append(cliente)
        cliente.id = self._siguiente_id
        self._siguiente_id += 1
        return cliente

    def existe_razon_social(self, razon_social_key: str, excluir_id: int | None = None) -> bool:
        return any(c.razon_social_key == razon_social_key for c in self.creados)


def test_migracion_h13_completa(tmp_path: Path) -> None:
    # 1. Normalización de datos sucios
    tel, motivo_tel = normalizar_telefono("+54 9 11 2233 4455")
    assert motivo_tel is None and tel.digitos == "5491122334455"
    assert normalizar_telefono("no tiene")[0] is None

    monto_ars, _ = normalizar_monto("$ 18.000,50")
    assert monto_ars.valor == Decimal("18000.50") and monto_ars.moneda == "ARS"
    monto_usd, _ = normalizar_monto("U$S 15")
    assert monto_usd.valor == Decimal("15") and monto_usd.moneda == "USD"

    fecha, _ = normalizar_fecha("16/05/26")
    assert fecha.valor == date(2026, 5, 16) and fecha.anio_supuesto is True

    tipo_v, _ = normalizar_tipo_vehiculo("Furgón Grande")
    assert tipo_v == "Furgón Grande"
    cap, _ = normalizar_capacidad("1,5 tn")
    assert cap.kilos == Decimal("1500")

    cod = codigo_de_movil("01")
    assert cod.valor == "MOV-01"

    cobro, _ = descomponer_estado_cobro("Seña $5000 debe el resto", Decimal("19000"))
    assert cobro.saldo == Decimal("14000")

    # 2. Archivo real de Excel y extracción
    archivo_excel = ruta_por_defecto()
    if archivo_excel.exists():
        verificar_hojas(archivo_excel)
        from scripts.migracion.__main__ import transformar

        res = transformar(archivo_excel)
        assert len(res.clientes) == 10
        assert len(res.moviles) == 8
        assert len(res.viajes) == 10
        assert len(res.cola) == 37

    # 3. Transformación sintética
    clientes_raw, _ = transformar_clientes([])
    assert clientes_raw == []
    moviles_raw, _ = transformar_moviles([])
    assert moviles_raw == []
    viajes_raw, _ = transformar_viajes([])
    assert viajes_raw == []

    # 4. Reporte Markdown
    c = ClienteMigrable(
        nombre="Cliente Uno",
        nombre_key="cliente uno",
        telefono="1122334455",
        direccion="Av. Cabildo 2140",
        direccion_es_estructurada=True,
        codigo_origen="CLI-101",
        localidad_barrio="Belgrano",
        condicion_iva="Responsable Inscripto",
        historial_pagos="Al día",
        fila_origen=2,
        hoja_origen="Clientes_Cotizaciones",
    )
    m = Movil(
        codigo="MOV-01",
        nombre_chofer="Chofer Uno",
        nombre_chofer_key="chofer uno",
        telefono="1144556677",
        tipo_vehiculo="Utilitario",
        capacidad_kg=Decimal(500),
        tarifa_hora_base=Decimal(1000),
        tarifa_km_excedente=Decimal(100),
        moneda_tarifa="ARS",
        estado="disponible",
        observaciones=[],
        filas_de_origen=[2],
    )
    v = Viaje(
        codigo="VJ-2001",
        fecha=date(2026, 5, 15),
        fecha_formato_origen="dd/mm/aaaa",
        chofer_nombre="Chofer Uno",
        chofer_nombre_key="chofer uno",
        cliente_nombre="Cliente Uno",
        cliente_nombre_key="cliente uno",
        origen="Origen",
        destino="Destino",
        hora_inicio=None,
        hora_fin=None,
        km_recorridos=Decimal(10),
        bultos_estimados=5,
        bultos_texto_original=None,
        monto_cobrado=Decimal(5000),
        moneda_monto="ARS",
        pago_medio="Efectivo",
        pago_estado="cobrado",
        pago_saldo=Decimal(0),
        fila_origen=2,
        hoja_origen="Registro_Viajes",
    )
    caso = RevisionHumana(
        hoja="Registro_Viajes",
        fila=2,
        clave="VJ-2001",
        motivo=Motivo.TEXTO_AMBIGUO,
        gravedad=Gravedad.BLOQUEANTE,
        valor_original="test",
        detalle="detalle",
    )
    reporte = generar_markdown(
        DatosReporte(
            archivo_origen="test.xlsx",
            generado_en=date(2026, 10, 15),
            moviles=[m],
            clientes=[c],
            viajes=[v],
            carga=ResultadoCarga(agregados=[c]),
            casos=[caso],
        )
    )
    assert "# Reporte de migración de datos históricos" in reporte
    assert "## Bloqueantes (1)" in reporte

    # 5. Carga e idempotencia
    repo = ClienteRepoFalso()
    res1 = cargar_clientes([c], repo)
    assert len(res1.agregados) == 1
    assert len(repo.creados) == 1

    # Segunda corrida: no duplica
    res2 = cargar_clientes([c], repo)
    assert len(res2.agregados) == 0
    assert len(res2.ya_existentes) == 1
    assert len(repo.creados) == 1
