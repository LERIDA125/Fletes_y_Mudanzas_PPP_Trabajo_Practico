class ReglaNegocioError(Exception):
    """Error base de las reglas de negocio del dominio.

    La capa de Presentación (app/api/) la traduce a un código HTTP.
    """


class RecursoNoEncontrado(ReglaNegocioError):
    """El recurso solicitado no existe o fue dado de baja (mapea a HTTP 404)."""


class ConflictoOperacion(ReglaNegocioError):
    """La operación entra en conflicto con el estado o unicidad de los datos (mapea a HTTP 409)."""


class DatoInvalido(ReglaNegocioError):
    """Los datos provistos son inválidos o no cumplen las reglas requeridas (mapea a HTTP 422)."""


# ── Clientes (H1) ─────────────────────────────────────────────────────────────


class ClienteNoEncontrado(RecursoNoEncontrado):
    def __init__(self, cliente_id: int) -> None:
        super().__init__(f"No existe un cliente con id {cliente_id}")
        self.cliente_id = cliente_id


class RazonSocialDuplicada(ConflictoOperacion):
    def __init__(self, razon_social: str) -> None:
        super().__init__(f"Ya existe un cliente con la razón social {razon_social!r}")
        self.razon_social = razon_social


class ClienteConHistorial(ConflictoOperacion):
    def __init__(self, cliente_id: int) -> None:
        super().__init__(
            f"El cliente {cliente_id} tiene servicios, cotizaciones o rendiciones asociadas "
            "y no se puede dar de baja"
        )
        self.cliente_id = cliente_id


# ── Vehículos y Tipos de Vehículo (H4) ──────────────────────────────────────────


class TipoVehiculoNoEncontrado(RecursoNoEncontrado):
    def __init__(self, tipo_vehiculo_id: int) -> None:
        super().__init__(f"No existe un tipo de vehículo con id {tipo_vehiculo_id}")
        self.tipo_vehiculo_id = tipo_vehiculo_id


class DescripcionDuplicada(ConflictoOperacion):
    def __init__(self, descripcion: str) -> None:
        super().__init__(f"Ya existe un tipo de vehículo con la descripción {descripcion!r}")
        self.descripcion = descripcion


class TipoVehiculoConVehiculos(ConflictoOperacion):
    def __init__(self, tipo_vehiculo_id: int) -> None:
        super().__init__(
            f"El tipo de vehículo {tipo_vehiculo_id} tiene vehículos asociados "
            "y no se puede dar de baja"
        )
        self.tipo_vehiculo_id = tipo_vehiculo_id


class VehiculoNoEncontrado(RecursoNoEncontrado):
    def __init__(self, vehiculo_id: int) -> None:
        super().__init__(f"No existe un vehículo con id {vehiculo_id}")
        self.vehiculo_id = vehiculo_id


class PatenteDuplicada(ConflictoOperacion):
    def __init__(self, patente: str) -> None:
        super().__init__(f"Ya existe un vehículo con la patente {patente!r}")
        self.patente = patente


class TipoVehiculoInvalido(DatoInvalido):
    def __init__(self, tipo_vehiculo_id: int) -> None:
        super().__init__(f"No existe un tipo de vehículo activo con id {tipo_vehiculo_id}")
        self.tipo_vehiculo_id = tipo_vehiculo_id


class ChoferInvalido(DatoInvalido):
    def __init__(self, chofer_id: int) -> None:
        super().__init__(f"No existe un chofer activo con id {chofer_id}")
        self.chofer_id = chofer_id


class VehiculoConServicios(ConflictoOperacion):
    def __init__(self, vehiculo_id: int) -> None:
        super().__init__(
            f"El vehículo {vehiculo_id} tiene servicios asociados y no se puede dar de baja"
        )
        self.vehiculo_id = vehiculo_id


# ── Choferes (H3) ──────────────────────────────────────────────────────────────


class ChoferNoEncontrado(RecursoNoEncontrado):
    def __init__(self, chofer_id: int) -> None:
        super().__init__(f"No existe un chofer con id {chofer_id}")
        self.chofer_id = chofer_id
