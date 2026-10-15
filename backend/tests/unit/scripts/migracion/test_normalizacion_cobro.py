"""Tests de la descomposición de `Estado_Cobro` (FR-028 a FR-031).

`Estado_Cobro` es una columna de texto libre que mezcla tres conceptos: medio de pago, estado del
cobro y saldo pendiente.
"""

from decimal import Decimal

from scripts.migracion import catalogos as cat
from scripts.migracion.normalizacion import descomponer_estado_cobro

MONTO = Decimal("10000")


class TestMedioDePago:
    def test_reconoce_el_medio_de_pago(self) -> None:
        casos = [
            ("Efectivo chofer en mano", cat.MEDIO_EFECTIVO),
            ("Pagó todo en mano", cat.MEDIO_EFECTIVO),
            ("Transferido completo", cat.MEDIO_TRANSFERENCIA),
            ("Transf pendiente", cat.MEDIO_TRANSFERENCIA),
            ("Cheque diferido", cat.MEDIO_CHEQUE),
        ]
        for entrada, esperado in casos:
            cobro, _ = descomponer_estado_cobro(entrada, MONTO)
            assert cobro.medio == esperado

    def test_un_medio_que_no_se_reconoce_no_se_fuerza(self) -> None:
        """FR-031: quedarse en `None` es correcto; elegir Efectivo sería inventar el dato."""
        for entrada in ["Anotado en la libreta", "Cta Cte", "Pagó mitad resta factura"]:
            cobro, motivos = descomponer_estado_cobro(entrada, MONTO)
            assert cobro.medio is None
            assert any("No se fuerza a Efectivo" in motivo for motivo in motivos)


class TestEstadoDelCobro:
    def test_reconoce_el_estado_del_cobro(self) -> None:
        casos = [
            ("Transferido completo", cat.COBRO_COBRADO),
            ("Pagó todo en mano", cat.COBRO_COBRADO),
            ("Transf pendiente", cat.COBRO_PENDIENTE),
            ("Cheque diferido", cat.COBRO_PENDIENTE),
            ("Pagó mitad resta factura", cat.COBRO_PARCIAL),
            ("Seña $5000 debe el resto", cat.COBRO_PARCIAL),
            ("Seña 50%", cat.COBRO_PARCIAL),
        ]
        for entrada, esperado in casos:
            cobro, _ = descomponer_estado_cobro(entrada, MONTO)
            assert cobro.estado == esperado

    def test_estados_ambiguos_o_indeterminados(self) -> None:
        cobro, _ = descomponer_estado_cobro("Pagó mitad resta factura", MONTO)
        assert cobro.estado == cat.COBRO_PARCIAL
        assert cobro.estado != cat.COBRO_COBRADO

        cobro_libreta, motivos = descomponer_estado_cobro("Anotado en la libreta", MONTO)
        assert cobro_libreta.estado is None
        assert any("quedó completo" in motivo for motivo in motivos)


class TestSaldo:
    def test_calculo_de_saldos(self) -> None:
        cobro_comp, _ = descomponer_estado_cobro("Transferido completo", MONTO)
        assert cobro_comp.saldo == Decimal(0)

        cobro_pend, _ = descomponer_estado_cobro("Transf pendiente", MONTO)
        assert cobro_pend.saldo == MONTO

        cobro_pesos, _ = descomponer_estado_cobro("Seña $5000 debe el resto", Decimal("19000"))
        assert cobro_pesos.saldo == Decimal("14000")

        cobro_porc, _ = descomponer_estado_cobro("Seña 50%", Decimal("26000"))
        assert cobro_porc.saldo == Decimal("13000.00")

        # Sin dato explícito o monto desconocido, queda en None
        assert descomponer_estado_cobro("Pagó mitad resta factura", MONTO)[0].saldo is None
        assert descomponer_estado_cobro("Seña $5000 debe el resto", None)[0].saldo is None
        assert descomponer_estado_cobro("Pagó parte", MONTO)[0].saldo is None


class TestCasosQueNoSePuedenMapear:
    def test_textos_ambiguos_y_casos_vacios(self) -> None:
        for entrada in list(cat.COBROS_AMBIGUOS):
            _, motivos = descomponer_estado_cobro(entrada, MONTO)
            explicacion = cat.COBROS_AMBIGUOS[entrada.lower()]
            assert any(explicacion in motivo for motivo in motivos)

        for vacio in [None, "", "   "]:
            cobro, motivos = descomponer_estado_cobro(vacio, MONTO)
            assert cobro.medio is None
            assert cobro.estado is None
            assert motivos

        cobro_orig, _ = descomponer_estado_cobro("Anotado en la libreta", MONTO)
        assert cobro_orig.monto_original == MONTO
