"""Repositorios en memoria para testear la capa de Aplicación sin PostgreSQL."""

from app.application.vehiculos.puertos import VehiculoRepository
from app.domain.vehiculo import Vehiculo


class VehiculoYaExiste(Exception):
    """Simula el error de base de datos cuando se viola el UNIQUE de patente."""


class FakeVehiculoRepo(VehiculoRepository):
    def __init__(self) -> None:
        self._por_id: dict[int, Vehiculo] = {}
        self._siguiente_id = 1
        self.llamadas_desactivar: list[int] = []

    def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        self._verificar_unicidad(vehiculo.patente)
        vehiculo.id = self._siguiente_id
        self._siguiente_id += 1
        self._por_id[vehiculo.id] = vehiculo
        return vehiculo

    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        return self._por_id.get(vehiculo_id)

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[Vehiculo]:
        candidatos = self._filtrar(busqueda)
        return candidatos[offset : offset + limit]

    def contar(self, busqueda: str | None) -> int:
        return len(self._filtrar(busqueda))

    def actualizar(self, vehiculo: Vehiculo) -> Vehiculo:
        self._verificar_unicidad(vehiculo.patente, excluir_id=vehiculo.id)
        self._por_id[vehiculo.id] = vehiculo
        return vehiculo

    def desactivar(self, vehiculo_id: int) -> None:
        self.llamadas_desactivar.append(vehiculo_id)
        self._por_id[vehiculo_id].desactivar()

    def existe_patente(self, patente: str, excluir_id: int | None = None) -> bool:
        return any(
            vehiculo.patente == patente and vehiculo.id != excluir_id
            for vehiculo in self._por_id.values()
        )

    def _filtrar(self, busqueda: str | None) -> list[Vehiculo]:
        activos = [vehiculo for vehiculo in self._por_id.values() if vehiculo.activo]
        if not busqueda:
            return sorted(activos, key=lambda vehiculo: vehiculo.id)
        return sorted(
            (vehiculo for vehiculo in activos if busqueda.upper() in vehiculo.patente),
            key=lambda vehiculo: vehiculo.id,
        )

    def _verificar_unicidad(self, patente: str, excluir_id: int | None = None) -> None:
        if self.existe_patente(patente, excluir_id=excluir_id):
            raise VehiculoYaExiste(patente)


class FakeConsultaTipoVehiculo:
    """Doble del puerto `ConsultaTipoVehiculo` para tests."""

    def __init__(self) -> None:
        self._tipos_activos: set[int] = set()
        self.consultas: list[int] = []

    def existe_activo(self, tipo_id: int) -> bool:
        self.consultas.append(tipo_id)
        return tipo_id in self._tipos_activos

    def marcar_activo(self, tipo_id: int) -> None:
        self._tipos_activos.add(tipo_id)


class FakeConsultaChofer:
    """Doble del puerto `ConsultaChofer` para tests."""

    def __init__(self) -> None:
        self._choferes_activos: set[int] = set()
        self.consultas: list[int] = []

    def existe_activo(self, chofer_id: int) -> bool:
        self.consultas.append(chofer_id)
        return chofer_id in self._choferes_activos

    def marcar_activo(self, chofer_id: int) -> None:
        self._choferes_activos.add(chofer_id)


class FakeConsultaServiciosVehiculo:
    """Doble del puerto `ConsultaServiciosVehiculo` para tests."""

    def __init__(self) -> None:
        self._vehiculos_con_servicios: set[int] = set()
        self.consultas: list[int] = []

    def tiene_servicios(self, vehiculo_id: int) -> bool:
        self.consultas.append(vehiculo_id)
        return vehiculo_id in self._vehiculos_con_servicios

    def marcar_con_servicios(self, vehiculo_id: int) -> None:
        self._vehiculos_con_servicios.add(vehiculo_id)
