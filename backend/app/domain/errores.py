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
