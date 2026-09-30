"""Exportación consolidada de schemas del sistema según el ERD."""

from app.api.schemas.chofer import ChoferCreate, ChoferRead, ChoferUpdate
from app.api.schemas.cliente import ClienteCreate, ClienteListado, ClienteRead, ClienteUpdate
from app.api.schemas.entrega import EntregaCreate, EntregaRead, EntregaUpdate
from app.api.schemas.equipamiento import (
    EquipamientoCreate,
    EquipamientoRead,
    EquipamientoUpdate,
    ServicioEquipamientoCreate,
    ServicioEquipamientoRead,
)
from app.api.schemas.pago import PagoCreate, PagoRead, PagoUpdate
from app.api.schemas.peon import (
    PeonCreate,
    PeonRead,
    PeonUpdate,
    ServicioPeonCreate,
    ServicioPeonRead,
)
from app.api.schemas.remito import RemitoCreate, RemitoRead
from app.api.schemas.rendicion import RendicionCreate, RendicionRead, RendicionUpdate
from app.api.schemas.servicio import (
    EstadoServicioRead,
    ServicioCreate,
    ServicioRead,
    ServicioUpdate,
)
from app.api.schemas.tipo_vehiculo import (
    TipoVehiculoCreate,
    TipoVehiculoRead,
    TipoVehiculoUpdate,
)
from app.api.schemas.vehiculo import VehiculoCreate, VehiculoRead, VehiculoUpdate
from app.api.schemas.zona import ZonaCreate, ZonaRead, ZonaUpdate

__all__ = [
    "ClienteCreate",
    "ClienteUpdate",
    "ClienteRead",
    "ClienteListado",
    "ChoferCreate",
    "ChoferUpdate",
    "ChoferRead",
    "TipoVehiculoCreate",
    "TipoVehiculoUpdate",
    "TipoVehiculoRead",
    "VehiculoCreate",
    "VehiculoUpdate",
    "VehiculoRead",
    "EstadoServicioRead",
    "ServicioCreate",
    "ServicioUpdate",
    "ServicioRead",
    "ZonaCreate",
    "ZonaUpdate",
    "ZonaRead",
    "EntregaCreate",
    "EntregaUpdate",
    "EntregaRead",
    "PeonCreate",
    "PeonUpdate",
    "PeonRead",
    "ServicioPeonCreate",
    "ServicioPeonRead",
    "EquipamientoCreate",
    "EquipamientoUpdate",
    "EquipamientoRead",
    "ServicioEquipamientoCreate",
    "ServicioEquipamientoRead",
    "PagoCreate",
    "PagoUpdate",
    "PagoRead",
    "RemitoCreate",
    "RemitoRead",
    "RendicionCreate",
    "RendicionUpdate",
    "RendicionRead",
]
