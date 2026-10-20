"""Stubs de consultas para historias futuras.

Estos stubs devuelven False para indicar que no hay dependencias que impidan
una operación. Se usan hasta que las historias correspondientes implementen
las consultas reales.

- ConsultaServiciosVehiculoVacio: hasta H6 (Servicios) — siempre False.

La consulta de choferes ya tiene implementación real (`ChoferRepo.existe_activo`), porque H3
completó la entidad Chofer.
"""


class ConsultaServiciosVehiculoVacio:
    """STUB temporal de ConsultaServiciosVehiculo. Devuelve False hasta H6."""

    def tiene_servicios(self, vehiculo_id: int) -> bool:
        return False
