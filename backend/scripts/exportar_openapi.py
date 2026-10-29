"""Vuelca el contrato OpenAPI de la API a un archivo JSON.

Es el insumo de `frontend/scripts/generar-tipos-api.mjs`, que convierte ese contrato en los
tipos TypeScript del cliente. No levanta el servidor de desarrollo ni abre la base de datos:
`app.openapi()` construye el esquema del documento a partir de los routers y los schemas
Pydantic, que son puro código. Por eso el tipo de la API puede regenerarse en la integración
continua sin servicios externos.

Uso (desde la raíz de `backend/`):

    python -m scripts.exportar_openapi [destino.json]

Sin destino escribe a la salida estándar.
"""

import json
import sys
from pathlib import Path

from app.main import app


def main() -> int:
    contrato = app.openapi()
    texto = json.dumps(contrato, ensure_ascii=False, indent=2) + "\n"

    if len(sys.argv) < 2:
        sys.stdout.write(texto)
        return 0

    destino = Path(sys.argv[1])
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
