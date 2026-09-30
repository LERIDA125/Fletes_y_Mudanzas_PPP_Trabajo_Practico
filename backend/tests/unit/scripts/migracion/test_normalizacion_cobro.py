"""Tests de la descomposición de `Estado_Cobro` (FR-028 a FR-031).

`Estado_Cobro` es una columna de texto libre que mezcla tres conceptos: medio de pago, estado del
cobro y saldo pendiente. El riesgo real acá es doble: declarar completo un cobro que no lo está, y
calcular un saldo que nadie escribió.
"""

from decimal import Decimal

import pytest

from scripts.migracion import catalogos as cat
from scripts.migracion.normalizacion import descomponer_estado_cobro

MONTO = Decimal("10000")


class TestMedioDePago:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("Efectivo chofer en mano", cat.MEDIO_EFECTIVO),
            ("Pagó todo en mano", cat.MEDIO_EFECTIVO),
            ("Transferido completo", cat.MEDIO_TRANSFERENCIA),
            ("Transf pendiente", cat.MEDIO_TRANSFERENCIA),
            ("Cheque diferido", cat.MEDIO_CHEQUE),
        ],
    )
    def test_reconoce_el_medio_de_pago(self, entrada: str, esperado: str) -> None:
        cobro, _ = descomponer_estado_cobro(entrada, MONTO)

        assert cobro.medio == esperado

    @pytest.mark.parametrize(
        "entrada", ["Anotado en la libreta", "Cta Cte", "Pagó mitad resta factura"]
    )
    def test_un_medio_que_no_se_reconoce_no_se_fuerza(self, entrada: str) -> None:
        """FR-031: quedarse en `None` es correcto; elegir Efectivo sería inventar el dato."""
        cobro, motivos = descomponer_estado_cobro(entrada, MONTO)

        assert cobro.medio is None
        assert any("No se fuerza a Efectivo" in motivo for motivo in motivos)

    def test_el_medio_desconocido_avisa_que_no_se_fuerza_a_ninguno(self) -> None:
        _, motivos = descomponer_estado_cobro("Anotado en la libreta", MONTO)

        assert any("No se fuerza a Efectivo" in motivo for motivo in motivos)


class TestEstadoDelCobro:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("Transferido completo", cat.COBRO_COBRADO),
            ("Pagó todo en mano", cat.COBRO_COBRADO),
            ("Transf pendiente", cat.COBRO_PENDIENTE),
            ("Cheque diferido", cat.COBRO_PENDIENTE),
            ("Pagó mitad resta factura", cat.COBRO_PARCIAL),
            ("Seña $5000 debe el resto", cat.COBRO_PARCIAL),
            ("Seña 50%", cat.COBRO_PARCIAL),
        ],
    )
    def test_reconoce_el_estado_del_cobro(self, entrada: str, esperado: str) -> None:
        cobro, _ = descomponer_estado_cobro(entrada, MONTO)

        assert cobro.estado == esperado

    def test_un_texto_que_dice_pago_sin_decir_pago_todo_no_es_cobro_completo(self) -> None:
        """FR-029: `Pagó mitad resta factura` dice "pagó" pero no está completo."""
        cobro, _ = descomponer_estado_cobro("Pagó mitad resta factura", MONTO)

        assert cobro.estado == cat.COBRO_PARCIAL
        assert cobro.estado != cat.COBRO_COBRADO

    def test_el_estado_indeterminado_no_se_asume(self) -> None:
        cobro, motivos = descomponer_estado_cobro("Anotado en la libreta", MONTO)

        assert cobro.estado is None
        assert any("quedó completo" in motivo for motivo in motivos)


class TestSaldo:
    def test_un_cobro_completo_deja_saldo_cero(self) -> None:
        cobro, _ = descomponer_estado_cobro("Transferido completo", MONTO)

        assert cobro.saldo == Decimal(0)

    def test_un_cobro_pendiente_deja_el_saldo_igual_al_monto(self) -> None:
        cobro, _ = descomponer_estado_cobro("Transf pendiente", MONTO)

        assert cobro.saldo == MONTO

    def test_una_sena_en_pesos_se_resta_del_monto(self) -> None:
        cobro, _ = descomponer_estado_cobro("Seña $5000 debe el resto", Decimal("19000"))

        assert cobro.saldo == Decimal("14000")

    def test_una_sena_en_porcentaje_se_calcula_sobre_el_monto(self) -> None:
        cobro, _ = descomponer_estado_cobro("Seña 50%", Decimal("26000"))

        assert cobro.saldo == Decimal("13000.00")

    def test_el_saldo_no_se_calcula_si_el_texto_no_lo_dice(self) -> None:
        """FR-030: sin dato explícito, el saldo queda sin calcular en vez de suponerse."""
        cobro, _ = descomponer_estado_cobro("Pagó mitad resta factura", MONTO)

        assert cobro.saldo is None

    def test_el_saldo_no_se_calcula_si_el_monto_es_desconocido(self) -> None:
        cobro, _ = descomponer_estado_cobro("Seña $5000 debe el resto", None)

        assert cobro.saldo is None

    def test_un_cobro_parcial_sin_monto_de_sena_deja_el_saldo_sin_calcular(self) -> None:
        cobro, _ = descomponer_estado_cobro("Pagó parte", MONTO)

        assert cobro.estado == cat.COBRO_PARCIAL
        assert cobro.saldo is None


class TestCasosQueNoSePuedenMapear:
    @pytest.mark.parametrize("entrada", list(cat.COBROS_AMBIGUOS))
    def test_todo_texto_conocido_ambiguo_avisa_por_que(self, entrada: str) -> None:
        """Cada caso ambiguo conocido explica su motivo, en vez de quedar como un `None` mudo."""
        _, motivos = descomponer_estado_cobro(entrada, MONTO)

        explicacion = cat.COBROS_AMBIGUOS[entrada.lower()]
        assert any(explicacion in motivo for motivo in motivos)

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_no_rompe(self, vacio) -> None:
        cobro, motivos = descomponer_estado_cobro(vacio, MONTO)

        assert cobro.medio is None
        assert cobro.estado is None
        assert motivos

    def test_el_monto_original_se_conserva_sin_importe_como_este(self) -> None:
        """El monto viaja en el cobro aunque el texto no diga nada del medio ni del estado."""
        cobro, _ = descomponer_estado_cobro("Anotado en la libreta", MONTO)

        assert cobro.monto_original == MONTO
