"""Repositorio en memoria para testear la capa de Aplicación sin PostgreSQL."""

from app.application.choferes.puertos import ChoferRepository
from app.domain.chofer import Chofer, normalizar_nombre


class FakeChoferRepo(ChoferRepository):
    def __init__(self) -> None:
        self._por_id: dict[int, Chofer] = {}
        self._siguiente_id = 1
        self.llamadas_desactivar: list[int] = []

    def crear(self, chofer: Chofer) -> Chofer:
        chofer.id = self._siguiente_id
        self._siguiente_id += 1
        self._por_id[chofer.id] = chofer
        return chofer

    def obtener_por_id(self, chofer_id: int) -> Chofer | None:
        return self._por_id.get(chofer_id)

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[Chofer]:
        candidatos = self._filtrar(busqueda)
        return candidatos[offset : offset + limit]

    def contar(self, busqueda: str | None) -> int:
        return len(self._filtrar(busqueda))

    def actualizar(self, chofer: Chofer) -> Chofer:
        self._por_id[chofer.id] = chofer
        return chofer

    def desactivar(self, chofer_id: int) -> None:
        self.llamadas_desactivar.append(chofer_id)
        self._por_id[chofer_id].desactivar()

    def _filtrar(self, busqueda: str | None) -> list[Chofer]:
        activos = [chofer for chofer in self._por_id.values() if chofer.activo]
        if not busqueda:
            return sorted(activos, key=lambda chofer: chofer.id)
        clave = normalizar_nombre(busqueda).lower()
        return sorted(
            (chofer for chofer in activos if clave in chofer.nombre_completo.lower()),
            key=lambda chofer: chofer.id,
        )
