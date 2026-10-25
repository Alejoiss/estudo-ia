"""Rotas de tutores."""

from fastapi import APIRouter, Response, status

from vetclinic.routers import ConnectionDependency
from vetclinic.schemas.faturas import InvoiceOutput
from vetclinic.schemas.pets import PetOutput
from vetclinic.schemas.tutores import TutorInput, TutorOutput
from vetclinic.services import tutores as tutor_service

router = APIRouter(prefix="/tutores", tags=["tutores"])


@router.post("", response_model=TutorOutput, status_code=status.HTTP_201_CREATED)
def create_tutor(data: TutorInput, connection: ConnectionDependency):
    """Cadastra um tutor."""
    return tutor_service.create_tutor(connection, data)


@router.get("", response_model=list[TutorOutput])
def list_tutors(connection: ConnectionDependency):
    """Lista os tutores."""
    return tutor_service.list_tutors(connection)


@router.get("/{tutor_id}", response_model=TutorOutput)
def get_tutor(tutor_id: int, connection: ConnectionDependency):
    """Consulta um tutor."""
    return tutor_service.get_tutor_or_raise(connection, tutor_id)


@router.put("/{tutor_id}", response_model=TutorOutput)
def replace_tutor(tutor_id: int, data: TutorInput, connection: ConnectionDependency):
    """Substitui os dados de um tutor."""
    return tutor_service.replace_tutor(connection, tutor_id, data)


@router.delete("/{tutor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tutor(tutor_id: int, connection: ConnectionDependency) -> Response:
    """Exclui um tutor sem pets."""
    tutor_service.delete_tutor(connection, tutor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{tutor_id}/pets", response_model=list[PetOutput])
def list_pets_of_tutor(tutor_id: int, connection: ConnectionDependency):
    """Lista os pets de um tutor."""
    return tutor_service.list_pets_of_tutor(connection, tutor_id)


@router.get("/{tutor_id}/faturas", response_model=list[InvoiceOutput])
def list_invoices_of_tutor(tutor_id: int, connection: ConnectionDependency):
    """Lista as faturas de um tutor."""
    return tutor_service.list_invoices_of_tutor(connection, tutor_id)
