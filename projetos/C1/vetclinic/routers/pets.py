"""Rotas de pets."""

from fastapi import APIRouter, Response, status

from vetclinic.routers import ConnectionDependency
from vetclinic.schemas.pets import PetInput, PetOutput
from vetclinic.services import pets as pet_service

router = APIRouter(prefix="/pets", tags=["pets"])


@router.post("", response_model=PetOutput, status_code=status.HTTP_201_CREATED)
def create_pet(data: PetInput, connection: ConnectionDependency):
    """Cadastra um pet."""
    return pet_service.create_pet(connection, data)


@router.get("/{pet_id}", response_model=PetOutput)
def get_pet(pet_id: int, connection: ConnectionDependency):
    """Consulta um pet."""
    return pet_service.get_pet_or_raise(connection, pet_id)


@router.put("/{pet_id}", response_model=PetOutput)
def replace_pet(pet_id: int, data: PetInput, connection: ConnectionDependency):
    """Substitui os dados de um pet."""
    return pet_service.replace_pet(connection, pet_id, data)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: int, connection: ConnectionDependency) -> Response:
    """Exclui um pet sem agendamentos."""
    pet_service.delete_pet(connection, pet_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
