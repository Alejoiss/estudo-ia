"""Rotas de veterinários."""

from fastapi import APIRouter, status

from vetclinic.routers import ConnectionDependency
from vetclinic.schemas.veterinarios import VeterinarianInput, VeterinarianOutput
from vetclinic.services import veterinarios as veterinarian_service

router = APIRouter(prefix="/veterinarios", tags=["veterinarios"])


@router.post("", response_model=VeterinarianOutput, status_code=status.HTTP_201_CREATED)
def create_veterinarian(data: VeterinarianInput, connection: ConnectionDependency):
    """Cadastra um veterinário."""
    return veterinarian_service.create_veterinarian(connection, data)


@router.get("", response_model=list[VeterinarianOutput])
def list_veterinarians(connection: ConnectionDependency):
    """Lista os veterinários."""
    return veterinarian_service.list_veterinarians(connection)


@router.get("/{veterinarian_id}", response_model=VeterinarianOutput)
def get_veterinarian(veterinarian_id: int, connection: ConnectionDependency):
    """Consulta um veterinário."""
    return veterinarian_service.get_veterinarian_or_raise(connection, veterinarian_id)
