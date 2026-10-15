"""Tests de la transformación (FR-009, FR-020, FR-021, FR-032).

Se prueban con `Fila` construidas a mano en vez del Excel: la transformación tiene que poder
testearse sin abrir el archivo, porque si dependiera del archivo no se podría probar un caso
aislado como el de los móviles duplicados.
"""

from scripts.migracion.extraccion import Fila
from scripts.migracion.revision import Gravedad, Motivo
from scripts.migracion.transformacion import (
    COLUMNAS_SIN_MAPEO_CLIENTE,
    aplicar_cruce,
    cruzar_viajes_con_choferes,
    transformar_clientes,
    transformar_moviles,
    transformar_viajes,
)

HOJA_CHOFERES = "Choferes_y_Moviles"
HOJA_CLIENTES = "Clientes_Cotizaciones"
HOJA_VIAJES = "Registro_Viajes"


def fila(hoja: str, numero: int, **datos) -> Fila:
    return Fila(hoja=hoja, numero=numero, datos=datos)


def fila_de_movil(numero: int, codigo: str, nombre: str, **extra) -> Fila:
    datos = {
        "Cod_Movil": codigo,
        "Nombre_Chofer": nombre,
        "Telefono_Contacto": "11-4455-6677",
        "Tipo_Vehiculo": "Furgon Grande",
        "Capacidad_Carga": "1500 kg",
        "Tarifa_Hora_Base": "$12.500",
        "Tarifa_Km_Excedente": "$450",
        "Estado_Actual": "Disponible",
    }
    datos.update(extra)
    return fila(HOJA_CHOFERES, numero, **datos)


def fila_de_cliente(numero: int, codigo: str, nombre: str, **extra) -> Fila:
    datos = {
        "ID_Cliente": codigo,
        "Nombre_o_Empresa": nombre,
        "Telefono": "11-2345-6789",
        "Direccion_Habitual": "Av. Cabildo 2140",
        "Localidad_Barrio": "Belgrano, CABA",
        "Condicion_IVA": "Responsable Inscripto",
        "Historial_Pagos": "Paga a 30 días",
    }
    datos.update(extra)
    return fila(HOJA_CLIENTES, numero, **datos)


def fila_de_viaje(numero: int, viaje: str, **extra) -> Fila:
    datos = {
        "Nro_Viaje": viaje,
        "Fecha_Servicio": "15/05/2026",
        "Chofer_Asignado": "Marcelo Rodriguez",
        "Cliente": "Muebles Belgrano S.R.L.",
        "Origen_Direccion": "Av. Cabildo 2140",
        "Destino_Direccion": "San Martin 1200",
        "Hora_Inicio": "08:30",
        "Hora_Fin": "12:00",
        "Km_Recorridos": "35,5",
        "Bultos_Estimados": "6 muebles embalados",
        "Monto_Cobrado": "$58.500",
        "Estado_Cobro": "Transferido completo",
    }
    datos.update(extra)
    return fila(HOJA_VIAJES, numero, **datos)


class TestTransformarMoviles:
    def test_un_codigo_repetido_con_otro_formato_es_el_mismo_movil(self) -> None:
        """FR-009: `MOV-01` y `MOV01` tienen que terminar en un solo móvil, no en dos."""
        moviles, cola = transformar_moviles(
            [
                fila_de_movil(2, "MOV-01", "Marcelo Rodriguez"),
                fila_de_movil(3, "MOV01", "MARCELO RODRIGUEZ"),
            ]
        )

        assert len(moviles) == 1
        assert moviles[0].codigo == "MOV-01"
        assert moviles[0].filas_de_origen == [2, 3]

    def test_el_duplicado_se_reporta_sin_elegir_cual_fila_manda(self) -> None:
        moviles, cola = transformar_moviles(
            [
                fila_de_movil(2, "MOV-01", "Marcelo Rodriguez"),
                fila_de_movil(3, "MOV01", "MARCELO RODRIGUEZ", Estado_Actual="En viaje"),
            ]
        )

        duplicados = [caso for caso in cola.casos if caso.motivo is Motivo.DUPLICADO]
        assert len(duplicados) == 1
        assert duplicados[0].gravedad is Gravedad.BLOQUEANTE
        assert "NO se decidió cuál es la vigente" in duplicados[0].detalle
        assert "estado" in duplicados[0].detalle

    def test_dos_nombres_diferentes_con_el_mismo_codigo_no_son_dos_moviles(self) -> None:
        moviles, cola = transformar_moviles(
            [
                fila_de_movil(7, "MOV-05", "Jorge 'El Negro'"),
                fila_de_movil(8, "MOV-05", "Jorge Almada"),
            ]
        )

        assert len(moviles) == 1
        assert moviles[0].nombre_chofer == "Jorge 'El Negro'"

    def test_las_anomalias_de_la_fila_que_no_gana_tambien_se_reportan(self) -> None:
        """El monto en dólares de la fila descartada tiene que aparecer igual en el reporte."""
        moviles, cola = transformar_moviles(
            [
                fila_de_movil(7, "MOV-05", "Jorge 'El Negro'"),
                fila_de_movil(8, "MOV-05", "Jorge Almada", Tarifa_Hora_Base="U$S 15"),
            ]
        )

        en_dolares = [caso for caso in cola.casos if caso.motivo is Motivo.MONEDA_EXTRANJERA]
        assert len(en_dolares) == 1
        assert en_dolares[0].fila == 8
        assert en_dolares[0].gravedad is Gravedad.BLOQUEANTE

    def test_un_codigo_ilegible_no_se_migra_y_se_reporta(self) -> None:
        moviles, cola = transformar_moviles([fila_de_movil(2, "sin codigo", "Alguien")])

        assert moviles == []
        assert any(caso.gravedad is Gravedad.BLOQUEANTE for caso in cola.casos)

    def test_los_moviles_salen_ordenados_por_codigo(self) -> None:
        moviles, _ = transformar_moviles(
            [
                fila_de_movil(2, "MOV-08", "Santi"),
                fila_de_movil(3, "MOV-02", "El Ruso"),
                fila_de_movil(4, "03", "Cacho"),
            ]
        )

        assert [movil.codigo for movil in moviles] == ["MOV-02", "MOV-03", "MOV-08"]

    def test_el_telefono_que_no_es_telefono_queda_ninguno_y_se_reporta(self) -> None:
        moviles, cola = transformar_moviles(
            [fila_de_movil(2, "MOV-06", "Tito", Telefono_Contacto="No tiene whatsapp")]
        )

        assert moviles[0].telefono is None
        assert any("no es un teléfono" in caso.detalle for caso in cola.casos)


class TestTransformarClientes:
    def test_la_transformacion_no_agrega_ningun_campo_de_cuenta_corriente(self) -> None:
        """FR-021 / DP-06: `Historial_Pagos` es una nota en palabras, no un dato estructurado.

        La garantía fuerte (que el `Cliente` se arme siempre con `tiene_cuenta_corriente=False`)
        está en `test_carga.py`, porque es ahí donde se construye la entidad. Acá se verifica
        que la transformación ni siquiera lleva un campo donde colgar ese booleano.
        """
        clientes, _ = transformar_clientes(
            [
                fila_de_cliente(
                    2, "CLI-101", "Muebles Belgrano S.R.L.", Historial_Pagos="Paga a 30 días"
                ),
                fila_de_cliente(
                    3, "CLI-102", "Panificadora Sur", Historial_Pagos="Cuenta corriente"
                ),
                fila_de_cliente(4, "CLI-103", "Gimnasio Iron", Historial_Pagos="Fiado de palabra"),
            ]
        )

        assert len(clientes) == 3
        assert not any(hasattr(cliente, "tiene_cuenta_corriente") for cliente in clientes)

    def test_el_historial_de_pagos_se_conserva_integro(self) -> None:
        clientes, _ = transformar_clientes(
            [
                fila_de_cliente(
                    2, "CLI-101", "Muebles Belgrano S.R.L.", Historial_Pagos="Fiado de palabra"
                )
            ]
        )

        assert clientes[0].historial_pagos == "Fiado de palabra"

    def test_una_direccion_no_estructurada_se_marca_y_no_se_inventa_una_direccion(self) -> None:
        clientes, cola = transformar_clientes(
            [
                fila_de_cliente(
                    6, "105", "Juan Carlos Gomez", Direccion_Habitual="Retira en depósito"
                )
            ]
        )

        assert clientes[0].direccion == "Retira en depósito"
        assert clientes[0].direccion_es_estructurada is False
        marcados = [c for c in cola.casos if c.motivo is Motivo.DIRECCION_NO_ESTRUCTURADA]
        assert len(marcados) == 1
        assert marcados[0].gravedad is Gravedad.BLOQUEANTE

    def test_las_columnas_sin_mapeo_se_reportan_una_vez_cada_una(self) -> None:
        """Se reportan por columna y no por celda, para que el reporte quede legible."""
        _, cola = transformar_clientes(
            [fila_de_cliente(2, "CLI-101", "Uno"), fila_de_cliente(3, "CLI-102", "Dos")]
        )

        sin_mapeo = [c for c in cola.casos if c.motivo is Motivo.SIN_MAPEO_EN_MODELO]
        claves = {caso.clave for caso in sin_mapeo}
        assert claves == {f"columna `{columna}`" for columna, _ in COLUMNAS_SIN_MAPEO_CLIENTE}

    def test_un_cliente_sin_nombre_no_se_migra(self) -> None:
        clientes, cola = transformar_clientes([fila_de_cliente(2, "CLI-101", "")])

        assert clientes == []
        assert any(caso.motivo is Motivo.DATO_INCOMPLETO for caso in cola.casos)

    def test_un_cliente_repetido_se_conserva_una_solo_vez(self) -> None:
        clientes, cola = transformar_clientes(
            [
                fila_de_cliente(2, "CLI-101", "Muebles Belgrano S.R.L."),
                fila_de_cliente(3, "CLI-101", "Muebles Belgrano S.R.L."),
            ]
        )

        assert len(clientes) == 1
        assert any(caso.motivo is Motivo.DUPLICADO_EN_ARCHIVO for caso in cola.casos)

    def test_un_prefijo_ausente_no_genera_un_cliente_distinto(self) -> None:
        """`102` y `CLI-102` tienen que ser el mismo cliente (FR-008)."""
        clientes, cola = transformar_clientes(
            [
                fila_de_cliente(2, "CLI-102", "Lucia Mendez"),
                fila_de_cliente(3, "102", "Lucia Mendez"),
            ]
        )

        assert len(clientes) == 1
        assert any(caso.motivo is Motivo.DUPLICADO_EN_ARCHIVO for caso in cola.casos)


class TestTransformarViajes:
    def test_normaliza_los_cuatro_formatos_de_fecha(self) -> None:
        viajes, _ = transformar_viajes(
            [
                fila_de_viaje(2, "VJ-2001", Fecha_Servicio="15/05/2026"),
                fila_de_viaje(3, "2002", Fecha_Servicio="2026-05-15"),
                fila_de_viaje(4, "2003", Fecha_Servicio="16 de Mayo 2026"),
                fila_de_viaje(5, "VJ-2004", Fecha_Servicio="16/05/26"),
            ]
        )

        assert [str(viaje.fecha) for viaje in viajes] == [
            "2026-05-15",
            "2026-05-15",
            "2026-05-16",
            "2026-05-16",
        ]

    def test_el_anio_supuesto_se_reporta(self) -> None:
        _, cola = transformar_viajes([fila_de_viaje(5, "VJ-2004", Fecha_Servicio="16/05/26")])

        assert any(caso.motivo is Motivo.SUPUESTO_DE_ANIO for caso in cola.casos)

    def test_un_bulto_sin_cantidad_queda_ninguno_y_conserva_el_texto(self) -> None:
        viajes, cola = transformar_viajes(
            [fila_de_viaje(4, "2003", Bultos_Estimados="Archivadores pesados")]
        )

        assert viajes[0].bultos_estimados is None
        assert viajes[0].bultos_texto_original == "Archivadores pesados"
        assert any(caso.motivo is Motivo.TEXTO_AMBIGUO for caso in cola.casos)

    def test_un_monto_en_dolares_no_se_convierte_y_se_reporta(self) -> None:
        viajes, cola = transformar_viajes([fila_de_viaje(2, "VJ-2001", Monto_Cobrado="U$S 100")])

        from scripts.migracion.normalizacion import MONEDA_DOLAR

        assert viajes[0].moneda_monto == MONEDA_DOLAR
        cambio = [c for c in cola.casos if c.motivo is Motivo.MONEDA_EXTRANJERA]
        assert len(cambio) == 1
        assert cambio[0].gravedad is Gravedad.BLOQUEANTE

    def test_un_numero_de_viaje_repetido_no_genera_dos_viajes(self) -> None:
        viajes, cola = transformar_viajes([fila_de_viaje(2, "VJ-2001"), fila_de_viaje(3, "2001")])

        assert len(viajes) == 1
        assert any(caso.motivo is Motivo.DUPLICADO_EN_ARCHIVO for caso in cola.casos)

    def test_una_fecha_ilegible_omite_la_fila_y_no_corta_el_resto(self) -> None:
        viajes, cola = transformar_viajes(
            [fila_de_viaje(2, "VJ-2001", Fecha_Servicio="el jueves"), fila_de_viaje(3, "VJ-2002")]
        )

        assert len(viajes) == 1
        assert viajes[0].codigo == "VJ-2002"
        assert any(caso.fila == 2 for caso in cola.casos)


class TestCruceViajesChoferes:
    def test_el_nombre_se_compara_sin_mayusculas_ni_acentos(self) -> None:
        """FR-032: `MARCELO RODRIGUEZ` y `Marcelo Rodriguez` son el mismo chofer."""
        moviles, _ = transformar_moviles([fila_de_movil(2, "MOV-01", "Marcelo Rodriguez")])
        viajes, _ = transformar_viajes(
            [fila_de_viaje(2, "VJ-2001", Chofer_Asignado="MARCELO RODRIGUEZ")]
        )

        mapa, casos = cruzar_viajes_con_choferes(viajes, moviles)
        aplicar_cruce(viajes, mapa)

        assert viajes[0].movil_codigo == "MOV-01"
        assert casos == []

    def test_un_chofer_que_no_esta_en_la_planilla_queda_sin_resolver(self) -> None:
        moviles, _ = transformar_moviles([fila_de_movil(2, "MOV-01", "Marcelo Rodriguez")])
        viajes, _ = transformar_viajes(
            [fila_de_viaje(2, "VJ-2001", Chofer_Asignado="Alguien Que No Existe")]
        )

        mapa, casos = cruzar_viajes_con_choferes(viajes, moviles)
        aplicar_cruce(viajes, mapa)

        assert viajes[0].movil_codigo is None
        assert len(casos) == 1
        assert casos[0].gravedad is Gravedad.A_CONFIRMAR

    def test_un_nombre_que_corresponde_a_dos_moviles_no_se_elige(self) -> None:
        moviles, _ = transformar_moviles(
            [
                fila_de_movil(2, "MOV-01", "Cacho"),
                fila_de_movil(3, "MOV-09", "Cacho Benitez Benito"),
            ]
        )
        # Dos móviles con el mismo nombre normalizado solo si son el mismo texto.
        moviles[1].nombre_chofer_key = moviles[0].nombre_chofer_key
        viajes, _ = transformar_viajes([fila_de_viaje(2, "VJ-2001", Chofer_Asignado="Cacho")])

        mapa, casos = cruzar_viajes_con_choferes(viajes, moviles)
        aplicar_cruce(viajes, mapa)

        assert viajes[0].movil_codigo is None
        assert casos[0].gravedad is Gravedad.BLOQUEANTE
