"""Puertos de la aplicación de cotización."""

from typing import Protocol, runtime_checkable

from app.domain.configuracion_cotizacion import ConfiguracionCotizacion
from app.domain.tipo_vehiculo import TipoVehiculo


@runtime_checkable
class ConsultaTipoVehiculoTarifas(Protocol):
    """Consulta las tarifas de un tipo de vehículo; implementación en infraestructura."""

    def obtener_por_id(self, tipo_id: int) -> TipoVehiculo | None: ...


@runtime_checkable
class ConsultaConfiguracionCotizacion(Protocol):
    """Consulta la configuración vigente de recargos; implementación en infraestructura."""

    def obtener(self) -> ConfiguracionCotizacion | None: ...
