"""Stubs de consultas para historias futuras.

Estos stubs devuelven False para indicar que no hay dependencias que impidan
una operación. Se usan hasta que las historias correspondientes implementen
las consultas reales.

- ConsultaVehiculosPorTipoVacia: hasta H4 (Vehículos) — siempre False.
- ConsultaTipoVehiculoVacio: hasta H4 (Vehículos) — siempre False.
- ConsultaChoferVacio: hasta H2 (Choferes) — siempre False.
- ConsultaServiciosVehiculoVacio: hasta H6 (Servicios) — siempre False.
"""


class ConsultaVehiculosPorTipoVacia:
    """STUB temporal de ConsultaVehiculosPorTipo. Devuelve False hasta H4."""

    def tiene_vehiculos(self, tipo_id: int) -> bool:
        return False


class ConsultaTipoVehiculoVacio:
    """STUB temporal de ConsultaTipoVehiculo. Devuelve False hasta H4."""

    def existe_activo(self, tipo_id: int) -> bool:
        return False


class ConsultaChoferVacio:
    """STUB temporal de ConsultaChofer. Devuelve False hasta H2."""

    def existe_activo(self, chofer_id: int) -> bool:
        return False


class ConsultaServiciosVehiculoVacio:
    """STUB temporal de ConsultaServiciosVehiculo. Devuelve False hasta H6."""

    def tiene_servicios(self, vehiculo_id: int) -> bool:
        return False
