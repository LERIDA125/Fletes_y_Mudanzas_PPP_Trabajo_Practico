from typing import Protocol, runtime_checkable

from app.domain.chofer import Chofer


@runtime_checkable
class ChoferRepository(Protocol):
    """Puerto de persistencia de choferes. Lo implementa app/infrastructure/.

    No hay `existe_*` porque ni el nombre ni el teléfono son únicos (DP-02/DP-04): los choferes
    se distinguen solo por su identificador.
    """

    def crear(self, chofer: Chofer) -> Chofer: ...

    def obtener_por_id(self, chofer_id: int) -> Chofer | None: ...

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[Chofer]: ...

    def contar(self, busqueda: str | None) -> int: ...

    def actualizar(self, chofer: Chofer) -> Chofer: ...

    def desactivar(self, chofer_id: int) -> None: ...
