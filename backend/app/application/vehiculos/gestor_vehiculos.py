from app.application.vehiculos.puertos import (
    ConsultaChofer,
    ConsultaServiciosVehiculo,
    ConsultaTipoVehiculo,
    VehiculoListadoItem,
    VehiculoRepository,
)
from app.domain.errores import (
    ChoferInvalido,
    PatenteDuplicada,
    TipoVehiculoInvalido,
    VehiculoConServicios,
    VehiculoNoEncontrado,
)
from app.domain.vehiculo import Vehiculo


class GestorVehiculos:
    """Reglas de negocio de vehículos (capa de Aplicación).

    Toda regla de H4 para vehículos vive acá: si el cliente cambia cómo se
    da de alta, edita o da de baja un vehículo, este es el único archivo
    que hay que tocar (AGENTS.md §2).
    """

    def __init__(
        self,
        repositorio_vehiculos: VehiculoRepository,
        consulta_tipos: ConsultaTipoVehiculo,
        consulta_choferes: ConsultaChofer,
        consulta_servicios: ConsultaServiciosVehiculo,
    ) -> None:
        self._repo = repositorio_vehiculos
        self._tipos = consulta_tipos
        self._choferes = consulta_choferes
        self._servicios = consulta_servicios

    def registrar(
        self,
        *,
        patente: str,
        id_tipo_vehiculo: int,
        id_chofer_habitual: int | None = None,
        usuario_id: int | None = None,
    ) -> Vehiculo:
        self._verificar_tipo_vehiculo(id_tipo_vehiculo)
        self._verificar_chofer_habitual(id_chofer_habitual)
        vehiculo = Vehiculo.crear(
            patente=patente,
            id_tipo_vehiculo=id_tipo_vehiculo,
            id_chofer_habitual=id_chofer_habitual,
            creado_por_id=usuario_id,
        )
        self._verificar_patente_disponible(vehiculo.patente)
        return self._repo.crear(vehiculo)

    def obtener(self, vehiculo_id: int) -> Vehiculo:
        vehiculo = self._repo.obtener_por_id(vehiculo_id)
        if vehiculo is None or not vehiculo.activo:
            raise VehiculoNoEncontrado(vehiculo_id)
        return vehiculo

    def listar(
        self, *, busqueda: str | None, offset: int, limit: int
    ) -> tuple[list[VehiculoListadoItem], int]:
        total = self._repo.contar(busqueda)
        return self._repo.listar(busqueda, offset, limit), total

    def actualizar(
        self,
        vehiculo_id: int,
        *,
        patente: str,
        id_tipo_vehiculo: int,
        id_chofer_habitual: int | None = None,
        usuario_id: int | None = None,
    ) -> Vehiculo:
        vehiculo = self.obtener(vehiculo_id)
        self._verificar_tipo_vehiculo(id_tipo_vehiculo)
        self._verificar_chofer_habitual(id_chofer_habitual)
        self._verificar_patente_disponible(
            Vehiculo(
                id=vehiculo_id,
                patente=patente,
                id_tipo_vehiculo=id_tipo_vehiculo,
                id_chofer_habitual=id_chofer_habitual,
            ).patente,
            excluir_id=vehiculo_id,
        )
        vehiculo.actualizar(
            patente=patente,
            id_tipo_vehiculo=id_tipo_vehiculo,
            id_chofer_habitual=id_chofer_habitual,
            modificado_por_id=usuario_id,
        )
        return self._repo.actualizar(vehiculo)

    def eliminar(self, vehiculo_id: int, *, usuario_id: int | None = None) -> None:
        vehiculo = self._repo.obtener_por_id(vehiculo_id)
        if vehiculo is None:
            raise VehiculoNoEncontrado(vehiculo_id)
        if not vehiculo.activo:
            return
        if self._servicios.tiene_servicios(vehiculo.id):
            raise VehiculoConServicios(vehiculo.id)
        vehiculo.desactivar(modificado_por_id=usuario_id)
        if usuario_id is not None:
            self._repo.actualizar(vehiculo)
        self._repo.desactivar(vehiculo.id)

    def _verificar_tipo_vehiculo(self, tipo_id: int) -> None:
        if not self._tipos.existe_activo(tipo_id):
            raise TipoVehiculoInvalido(tipo_id)

    def _verificar_chofer_habitual(self, chofer_id: int | None) -> None:
        if chofer_id is not None and not self._choferes.existe_activo(chofer_id):
            raise ChoferInvalido(chofer_id)

    def _verificar_patente_disponible(self, patente: str, excluir_id: int | None = None) -> None:
        if self._repo.existe_patente(patente, excluir_id=excluir_id):
            raise PatenteDuplicada(patente)
