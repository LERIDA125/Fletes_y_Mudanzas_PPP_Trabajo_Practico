"""Stubs de consultas para historias futuras.

Estos stubs devuelven False para indicar que no hay dependencias que impidan
una operación. Se usan hasta que las historias correspondientes implementen
las consultas reales.

- ConsultaChoferVacio: hasta H2 (Choferes) — siempre False.
- ConsultaServiciosVehiculoVacio: hasta H6 (Servicios) — siempre False.
"""


class ConsultaChoferVacio:
    """STUB temporal de ConsultaChofer. Devuelve False hasta H2."""

    def existe_activo(self, chofer_id: int) -> bool:
        return False


class ConsultaServiciosVehiculoVacio:
    """STUB temporal de ConsultaServiciosVehiculo. Devuelve False hasta H6."""

    def tiene_servicios(self, vehiculo_id: int) -> bool:
        return False
