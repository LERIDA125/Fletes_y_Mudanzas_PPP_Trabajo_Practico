from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errores import ServicioConDependencias, ServicioNoEncontrado
from app.infrastructure.repositories.servicio_repo import ServicioRepo


def test_eliminar_rechaza_servicio_inexistente() -> None:
    db = Mock(spec=Session)
    db.get.return_value = None

    with pytest.raises(ServicioNoEncontrado):
        ServicioRepo(db).eliminar(42)

    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_eliminar_retrocede_y_reporta_dependencias_referenciales() -> None:
    db = Mock(spec=Session)
    db.get.return_value = object()
    db.commit.side_effect = IntegrityError("DELETE", {}, RuntimeError("foreign key"))

    with pytest.raises(ServicioConDependencias):
        ServicioRepo(db).eliminar(42)

    db.rollback.assert_called_once()
