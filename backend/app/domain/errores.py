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


class ClienteInvalido(DatoInvalido):
    def __init__(self, cliente_id: int) -> None:
        super().__init__(f"No existe un cliente activo con id {cliente_id}")
        self.cliente_id = cliente_id


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


class VehiculoInvalido(DatoInvalido):
    def __init__(self, vehiculo_id: int) -> None:
        super().__init__(f"No existe un vehículo activo con id {vehiculo_id}")
        self.vehiculo_id = vehiculo_id


class VehiculoTipoIncompatible(DatoInvalido):
    def __init__(self, vehiculo_id: int, tipo_vehiculo_id: int) -> None:
        super().__init__(
            f"El vehículo {vehiculo_id} no pertenece al tipo de vehículo {tipo_vehiculo_id}"
        )
        self.vehiculo_id = vehiculo_id
        self.tipo_vehiculo_id = tipo_vehiculo_id


class TransicionEstadoServicioInvalida(DatoInvalido):
    def __init__(self, estado_actual: str, estado_solicitado: str) -> None:
        super().__init__(f"No se puede pasar el servicio de {estado_actual} a {estado_solicitado}")
        self.estado_actual = estado_actual
        self.estado_solicitado = estado_solicitado


class ServicioNoEncontrado(RecursoNoEncontrado):
    def __init__(self, servicio_id: int) -> None:
        super().__init__(f"No existe un servicio con id {servicio_id}")
        self.servicio_id = servicio_id


class ServicioNoCancelable(ConflictoOperacion):
    def __init__(self, estado_actual: str) -> None:
        super().__init__(f"Un servicio en estado {estado_actual!r} no se puede cancelar")
        self.estado_actual = estado_actual


class MotivoCancelacionObligatorio(DatoInvalido):
    def __init__(self) -> None:
        super().__init__("El motivo de cancelación es obligatorio")


class ReferenciasServicioInvalidas(DatoInvalido):
    def __init__(self) -> None:
        super().__init__(
            "Una entidad relacionada dejó de estar disponible al registrar el servicio"
        )


# ── Choferes (H3) ──────────────────────────────────────────────────────────────


class ChoferNoEncontrado(RecursoNoEncontrado):
    def __init__(self, chofer_id: int) -> None:
        super().__init__(f"No existe un chofer con id {chofer_id}")
        self.chofer_id = chofer_id
