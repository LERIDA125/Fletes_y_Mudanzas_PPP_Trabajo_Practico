from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.choferes import router as choferes_router
from app.api.clientes import router as clientes_router
from app.api.tipos_vehiculo import router as tipos_vehiculo_router
from app.api.vehiculos import router as vehiculos_router
from app.domain.errores import (
    ConflictoOperacion,
    DatoInvalido,
    RecursoNoEncontrado,
    ReglaNegocioError,
)

app = FastAPI(
    title="Fletes y Mudanzas Express API",
    version="0.1.0",
    description="API del sistema de gestión de Fletes y Mudanzas Express.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["sistema"], summary="Verificar que la API está viva")
def health() -> dict[str, str]:
    return {"estado": "ok"}


# Traducción polimórfica de errores de Dominio a códigos HTTP (AGENTS.md §2).
# Se agrupan por clase base para evitar duplicar handlers por cada entidad nueva.
@app.exception_handler(RecursoNoEncontrado)
async def recurso_no_encontrado(_request: Request, error: RecursoNoEncontrado) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


@app.exception_handler(ConflictoOperacion)
async def conflicto_operacion(_request: Request, error: ConflictoOperacion) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )


@app.exception_handler(DatoInvalido)
async def dato_invalido(_request: Request, error: DatoInvalido) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(error)},
    )


@app.exception_handler(ReglaNegocioError)
async def regla_de_negocio(_request: Request, error: ReglaNegocioError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(error)},
    )


app.include_router(clientes_router)
app.include_router(choferes_router)
app.include_router(tipos_vehiculo_router)
app.include_router(vehiculos_router)
