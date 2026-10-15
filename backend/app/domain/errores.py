class ReglaNegocioError(Exception):
    """Error base de las reglas de negocio del dominio.

    La capa de Presentación (app/api/) la traduce a un código HTTP.
    """


class ClienteNoEncontrado(ReglaNegocioError):
    def __init__(self, cliente_id: int) -> None:
        super().__init__(f"No existe un cliente con id {cliente_id}")
        self.cliente_id = cliente_id


class RazonSocialDuplicada(ReglaNegocioError):
    def __init__(self, razon_social: str) -> None:
        super().__init__(f"Ya existe un cliente con la razón social {razon_social!r}")
        self.razon_social = razon_social


class ClienteConHistorial(ReglaNegocioError):
    def __init__(self, cliente_id: int) -> None:
        super().__init__(
            f"El cliente {cliente_id} tiene servicios, cotizaciones o rendiciones asociadas "
            "y no se puede dar de baja"
        )
        self.cliente_id = cliente_id


# ── H4: Vehículos y Tipos de Vehículo ──────────────────────────────────────────


class TipoVehiculoNoEncontrado(ReglaNegocioError):
    def __init__(self, tipo_vehiculo_id: int) -> None:
        super().__init__(f"No existe un tipo de vehículo con id {tipo_vehiculo_id}")
        self.tipo_vehiculo_id = tipo_vehiculo_id


class DescripcionDuplicada(ReglaNegocioError):
    def __init__(self, descripcion: str) -> None:
        super().__init__(f"Ya existe un tipo de vehículo con la descripción {descripcion!r}")
        self.descripcion = descripcion


class TipoVehiculoConVehiculos(ReglaNegocioError):
    def __init__(self, tipo_vehiculo_id: int) -> None:
        super().__init__(
            f"El tipo de vehículo {tipo_vehiculo_id} tiene vehículos asociados "
            "y no se puede dar de baja"
        )
        self.tipo_vehiculo_id = tipo_vehiculo_id


class VehiculoNoEncontrado(ReglaNegocioError):
    def __init__(self, vehiculo_id: int) -> None:
        super().__init__(f"No existe un vehículo con id {vehiculo_id}")
        self.vehiculo_id = vehiculo_id


class PatenteDuplicada(ReglaNegocioError):
    def __init__(self, patente: str) -> None:
        super().__init__(f"Ya existe un vehículo con la patente {patente!r}")
        self.patente = patente


class TipoVehiculoInvalido(ReglaNegocioError):
    def __init__(self, tipo_vehiculo_id: int) -> None:
        super().__init__(f"No existe un tipo de vehículo activo con id {tipo_vehiculo_id}")
        self.tipo_vehiculo_id = tipo_vehiculo_id


class ChoferInvalido(ReglaNegocioError):
    def __init__(self, chofer_id: int) -> None:
        super().__init__(f"No existe un chofer activo con id {chofer_id}")
        self.chofer_id = chofer_id


class VehiculoConServicios(ReglaNegocioError):
    def __init__(self, vehiculo_id: int) -> None:
        super().__init__(
            f"El vehículo {vehiculo_id} tiene servicios asociados "
            "y no se puede dar de baja"
        )
        self.vehiculo_id = vehiculo_id
