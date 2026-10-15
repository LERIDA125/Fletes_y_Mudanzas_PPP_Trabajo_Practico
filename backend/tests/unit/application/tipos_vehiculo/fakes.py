"""Repositorios en memoria para testear la capa de Aplicación sin PostgreSQL."""

from app.application.tipos_vehiculo.puertos import TipoVehiculoRepository
from app.domain.tipo_vehiculo import TipoVehiculo


class TipoVehiculoYaExiste(Exception):
    """Simula el error de base de datos cuando se viola el UNIQUE de descripcion_key."""


class FakeTipoVehiculoRepo(TipoVehiculoRepository):
    def __init__(self) -> None:
        self._por_id: dict[int, TipoVehiculo] = {}
        self._siguiente_id = 1
        self.llamadas_desactivar: list[int] = []

    def crear(self, tipo: TipoVehiculo) -> TipoVehiculo:
        self._verificar_unicidad(tipo.descripcion_key)
        tipo.id = self._siguiente_id
        self._siguiente_id += 1
        self._por_id[tipo.id] = tipo
        return tipo

    def obtener_por_id(self, tipo_id: int) -> TipoVehiculo | None:
        return self._por_id.get(tipo_id)

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[TipoVehiculo]:
        candidatos = self._filtrar(busqueda)
        return candidatos[offset : offset + limit]

    def contar(self, busqueda: str | None) -> int:
        return len(self._filtrar(busqueda))

    def actualizar(self, tipo: TipoVehiculo) -> TipoVehiculo:
        self._verificar_unicidad(tipo.descripcion_key, excluir_id=tipo.id)
        self._por_id[tipo.id] = tipo
        return tipo

    def desactivar(self, tipo_id: int) -> None:
        self.llamadas_desactivar.append(tipo_id)
        self._por_id[tipo_id].desactivar()

    def existe_descripcion(self, descripcion_key: str, excluir_id: int | None = None) -> bool:
        return any(
            tipo.descripcion_key == descripcion_key and tipo.id != excluir_id
            for tipo in self._por_id.values()
        )

    def _filtrar(self, busqueda: str | None) -> list[TipoVehiculo]:
        from app.domain.tipo_vehiculo import normalizar_descripcion_key

        activos = [tipo for tipo in self._por_id.values() if tipo.activo]
        if not busqueda:
            return sorted(activos, key=lambda tipo: tipo.id)
        clave = normalizar_descripcion_key(busqueda)
        return sorted(
            (tipo for tipo in activos if clave in tipo.descripcion_key),
            key=lambda tipo: tipo.id,
        )

    def _verificar_unicidad(self, descripcion_key: str, excluir_id: int | None = None) -> None:
        if self.existe_descripcion(descripcion_key, excluir_id=excluir_id):
            raise TipoVehiculoYaExiste(descripcion_key)


class FakeConsultaVehiculosPorTipo:
    """Doble del puerto `ConsultaVehiculosPorTipo` para tests."""

    def __init__(self) -> None:
        self._tipos_con_vehiculos: set[int] = set()
        self.consultas: list[int] = []

    def tiene_vehiculos(self, tipo_id: int) -> bool:
        self.consultas.append(tipo_id)
        return tipo_id in self._tipos_con_vehiculos

    def marcar_con_vehiculos(self, tipo_id: int) -> None:
        self._tipos_con_vehiculos.add(tipo_id)
