from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.clientes import router as clientes_router
from app.domain.errores import (
    ClienteConHistorial,
    ClienteNoEncontrado,
    RazonSocialDuplicada,
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


# Traducción de los errores de Dominio a códigos HTTP. Vive acá y no en los routers para que cada
# regla de negocio se traduzca siempre igual, sin repetir el mapeo ruta por ruta.
# Starlette busca el handler recorriendo la jerarquía de la excepción, así que los handlers de las
# clases concretas ganan sobre el de `ReglaNegocioError`.
@app.exception_handler(ClienteNoEncontrado)
async def cliente_no_encontrado(_request: Request, error: ClienteNoEncontrado) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


@app.exception_handler(RazonSocialDuplicada)
async def razon_social_duplicada(_request: Request, error: RazonSocialDuplicada) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )


@app.exception_handler(ClienteConHistorial)
async def cliente_con_historial(_request: Request, error: ClienteConHistorial) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )


@app.exception_handler(ReglaNegocioError)
async def regla_de_negocio(_request: Request, error: ReglaNegocioError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(error)},
    )


app.include_router(clientes_router)
