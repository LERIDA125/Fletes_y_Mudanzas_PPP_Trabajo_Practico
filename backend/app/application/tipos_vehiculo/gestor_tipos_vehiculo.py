from app.application.tipos_vehiculo.puertos import (
    ConsultaVehiculosPorTipo,
    TipoVehiculoRepository,
)
from app.domain.errores import (
    DescripcionDuplicada,
    TipoVehiculoConVehiculos,
    TipoVehiculoNoEncontrado,
)
from app.domain.tipo_vehiculo import TipoVehiculo


class GestorTiposVehiculo:
    """Reglas de negocio de tipos de vehículo (capa de Aplicación).

    Toda regla de H4 para tipos de vehículo vive acá: si el cliente cambia cómo se
    da de alta, edita o da de baja un tipo de vehículo, este es el único archivo
    que hay que tocar (AGENTS.md §2).
    """

    def __init__(
        self,
        repositorio_tipos: TipoVehiculoRepository,
        consulta_vehiculos: ConsultaVehiculosPorTipo,
    ) -> None:
        self._repo = repositorio_tipos
        self._vehiculos = consulta_vehiculos

    def registrar(
        self,
        *,
        descripcion: str,
        capacidad_carga_kg: float,
        tarifa_hora_base: float,
        tarifa_km_excedente: float,
    ) -> TipoVehiculo:
        from decimal import Decimal

        tipo = TipoVehiculo.crear(
            descripcion=descripcion,
            capacidad_carga_kg=Decimal(str(capacidad_carga_kg)),
            tarifa_hora_base=Decimal(str(tarifa_hora_base)),
            tarifa_km_excedente=Decimal(str(tarifa_km_excedente)),
        )
        self._verificar_descripcion_disponible(tipo.descripcion_key)
        return self._repo.crear(tipo)

    def obtener(self, tipo_id: int) -> TipoVehiculo:
        tipo = self._repo.obtener_por_id(tipo_id)
        if tipo is None or not tipo.activo:
            raise TipoVehiculoNoEncontrado(tipo_id)
        return tipo

    def listar(
        self, *, busqueda: str | None, offset: int, limit: int
    ) -> tuple[list[TipoVehiculo], int]:
        total = self._repo.contar(busqueda)
        return self._repo.listar(busqueda, offset, limit), total

    def actualizar(
        self,
        tipo_id: int,
        *,
        descripcion: str,
        capacidad_carga_kg: float,
        tarifa_hora_base: float,
        tarifa_km_excedente: float,
    ) -> TipoVehiculo:
        from decimal import Decimal

        tipo = self.obtener(tipo_id)
        self._verificar_descripcion_disponible(
            TipoVehiculo(
                id=tipo_id,
                descripcion=descripcion,
                capacidad_carga_kg=Decimal(str(capacidad_carga_kg)),
                tarifa_hora_base=Decimal(str(tarifa_hora_base)),
                tarifa_km_excedente=Decimal(str(tarifa_km_excedente)),
            ).descripcion_key,
            excluir_id=tipo_id,
        )
        tipo.actualizar(
            descripcion=descripcion,
            capacidad_carga_kg=Decimal(str(capacidad_carga_kg)),
            tarifa_hora_base=Decimal(str(tarifa_hora_base)),
            tarifa_km_excedente=Decimal(str(tarifa_km_excedente)),
        )
        return self._repo.actualizar(tipo)

    def eliminar(self, tipo_id: int) -> None:
        tipo = self._repo.obtener_por_id(tipo_id)
        if tipo is None:
            raise TipoVehiculoNoEncontrado(tipo_id)
        if not tipo.activo:
            return
        if self._vehiculos.tiene_vehiculos(tipo.id):
            raise TipoVehiculoConVehiculos(tipo.id)
        tipo.desactivar()
        self._repo.desactivar(tipo.id)

    def _verificar_descripcion_disponible(
        self, descripcion_key: str, excluir_id: int | None = None
    ) -> None:
        if self._repo.existe_descripcion(descripcion_key, excluir_id=excluir_id):
            raise DescripcionDuplicada(descripcion_key)
