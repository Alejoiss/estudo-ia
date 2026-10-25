"""Fábrica da aplicação FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from vetclinic.config import load_settings
from vetclinic.database import initialize_schema
from vetclinic.errors import (
    DomainError,
    InvalidDataError,
    ResourceNotFoundError,
    StateConflictError,
)
from vetclinic.routers import (
    agendamentos,
    atendimentos,
    faturas,
    pets,
    produtos,
    tutores,
    veterinarios,
)

ROUTER_MODULES = (
    tutores,
    pets,
    veterinarios,
    produtos,
    agendamentos,
    atendimentos,
    faturas,
)

STATUS_CODE_BY_DOMAIN_ERROR: dict[type[DomainError], int] = {
    ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
    StateConflictError: status.HTTP_409_CONFLICT,
    InvalidDataError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


async def _handle_domain_error(_request: Request, error: DomainError) -> JSONResponse:
    """Converte uma falha de domínio em `{"detail": mensagem}` com o status adequado."""
    status_code = STATUS_CODE_BY_DOMAIN_ERROR[type(error)]
    return JSONResponse(status_code=status_code, content={"detail": error.message})


@asynccontextmanager
async def _lifespan(_application: FastAPI) -> AsyncIterator[None]:
    """Cria as tabelas na inicialização, se ainda não existirem."""
    initialize_schema(load_settings().database_path)
    yield


def create_application() -> FastAPI:
    """Monta a aplicação com rotas e tratadores de erro."""
    application = FastAPI(title="VetClinic API", lifespan=_lifespan)
    for error_type in STATUS_CODE_BY_DOMAIN_ERROR:
        application.add_exception_handler(error_type, _handle_domain_error)
    for module in ROUTER_MODULES:
        application.include_router(module.router)
    return application
