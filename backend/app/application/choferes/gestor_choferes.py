from app.application.choferes.puertos import ChoferRepository
from app.domain.chofer import Chofer
from app.domain.errores import ChoferNoEncontrado


class GestorChoferes:
    """Reglas de negocio de choferes (capa de Aplicación).

    Toda regla de H3 vive acá: si el cliente cambia cómo se da de alta, edita o da de baja un
    chofer, este es el único archivo que hay que tocar (AGENTS.md §2).
    """

    def __init__(self, repositorio_choferes: ChoferRepository) -> None:
        self._repo = repositorio_choferes

    def registrar(self, *, nombre_completo: str, telefono: str) -> Chofer:
        chofer = Chofer.crear(nombre_completo=nombre_completo, telefono=telefono)
        return self._repo.crear(chofer)

    def obtener(self, chofer_id: int) -> Chofer:
        chofer = self._repo.obtener_por_id(chofer_id)
        if chofer is None or not chofer.activo:
            raise ChoferNoEncontrado(chofer_id)
        return chofer

    def listar(self, *, busqueda: str | None, offset: int, limit: int) -> tuple[list[Chofer], int]:
        total = self._repo.contar(busqueda)
        return self._repo.listar(busqueda, offset, limit), total

    def actualizar(self, chofer_id: int, *, nombre_completo: str, telefono: str) -> Chofer:
        chofer = self.obtener(chofer_id)
        chofer.actualizar(nombre_completo=nombre_completo, telefono=telefono)
        return self._repo.actualizar(chofer)

    def eliminar(self, chofer_id: int) -> None:
        chofer = self._repo.obtener_por_id(chofer_id)
        if chofer is None:
            raise ChoferNoEncontrado(chofer_id)
        if not chofer.activo:
            return
        chofer.desactivar()
        self._repo.desactivar(chofer.id)
