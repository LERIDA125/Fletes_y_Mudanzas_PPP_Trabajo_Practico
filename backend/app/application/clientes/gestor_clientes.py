from app.application.clientes.puertos import ClienteRepository, ConsultaHistorialCliente
from app.domain.cliente import Cliente
from app.domain.errores import ClienteConHistorial, ClienteNoEncontrado, RazonSocialDuplicada


class GestorClientes:
    """Reglas de negocio de clientes (capa de Aplicación).

    Toda regla de H1 vive acá: si el cliente cambia cómo se da de alta, edita o da de baja un
    cliente, este es el único archivo que hay que tocar (AGENTS.md §2).
    """

    def __init__(
        self,
        repositorio_clientes: ClienteRepository,
        consulta_historial: ConsultaHistorialCliente,
    ) -> None:
        self._repo = repositorio_clientes
        self._historial = consulta_historial

    def registrar(
        self,
        *,
        razon_social: str,
        telefono: str,
        direccion_habitual: str,
        tiene_cuenta_corriente: bool,
    ) -> Cliente:
        cliente = Cliente.crear(
            razon_social=razon_social,
            telefono=telefono,
            direccion_habitual=direccion_habitual,
            tiene_cuenta_corriente=tiene_cuenta_corriente,
        )
        self._verificar_razon_social_disponible(cliente.razon_social_key)
        return self._repo.crear(cliente)

    def obtener(self, cliente_id: int) -> Cliente:
        cliente = self._repo.obtener_por_id(cliente_id)
        if cliente is None or not cliente.activo:
            raise ClienteNoEncontrado(cliente_id)
        return cliente

    def listar(self, *, busqueda: str | None, offset: int, limit: int) -> tuple[list[Cliente], int]:
        total = self._repo.contar(busqueda)
        return self._repo.listar(busqueda, offset, limit), total

    def actualizar(
        self,
        cliente_id: int,
        *,
        razon_social: str,
        telefono: str,
        direccion_habitual: str,
        tiene_cuenta_corriente: bool,
    ) -> Cliente:
        cliente = self.obtener(cliente_id)
        self._verificar_razon_social_disponible(
            Cliente(  # se normaliza antes de comparar, sin tocar el cliente guardado
                id=cliente_id,
                razon_social=razon_social,
                telefono=telefono,
                direccion_habitual=direccion_habitual,
                tiene_cuenta_corriente=tiene_cuenta_corriente,
            ).razon_social_key,
            excluir_id=cliente_id,
        )
        cliente.actualizar(
            razon_social=razon_social,
            telefono=telefono,
            direccion_habitual=direccion_habitual,
            tiene_cuenta_corriente=tiene_cuenta_corriente,
        )
        return self._repo.actualizar(cliente)

    def eliminar(self, cliente_id: int) -> None:
        cliente = self._repo.obtener_por_id(cliente_id)
        if cliente is None:
            raise ClienteNoEncontrado(cliente_id)
        if not cliente.activo:
            return
        if self._historial.tiene_historial(cliente.id):
            raise ClienteConHistorial(cliente.id)
        cliente.desactivar()
        self._repo.desactivar(cliente.id)

    def _verificar_razon_social_disponible(
        self, razon_social_key: str, excluir_id: int | None = None
    ) -> None:
        if self._repo.existe_razon_social(razon_social_key, excluir_id=excluir_id):
            raise RazonSocialDuplicada(razon_social_key)
