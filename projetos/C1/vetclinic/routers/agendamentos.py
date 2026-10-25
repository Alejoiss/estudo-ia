"""Rotas de agendamentos e do atendimento associado a eles."""

from fastapi import APIRouter, Body, status

from vetclinic.routers import ConnectionDependency
from vetclinic.schemas.agendamentos import (
    AppointmentInput,
    AppointmentOutput,
    CancellationInput,
)
from vetclinic.schemas.atendimentos import TreatmentInput, TreatmentOutput
from vetclinic.services import agendamentos as appointment_service
from vetclinic.services import atendimentos as treatment_service
from vetclinic.validation import DateText

router = APIRouter(prefix="/agendamentos", tags=["agendamentos"])


@router.post("", response_model=AppointmentOutput, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentInput, connection: ConnectionDependency):
    """Cria um agendamento."""
    return appointment_service.create_appointment(connection, data)


@router.get("", response_model=list[AppointmentOutput])
def list_appointments(
    connection: ConnectionDependency,
    veterinario_id: int | None = None,
    data: DateText | None = None,
):
    """Lista agendamentos, com filtros opcionais por veterinário e dia."""
    return appointment_service.list_appointments(connection, veterinario_id, data)


@router.get("/{appointment_id}", response_model=AppointmentOutput)
def get_appointment(appointment_id: int, connection: ConnectionDependency):
    """Consulta um agendamento."""
    return appointment_service.get_appointment_or_raise(connection, appointment_id)


@router.post("/{appointment_id}/cancelar", response_model=AppointmentOutput)
def cancel_appointment(
    appointment_id: int,
    connection: ConnectionDependency,
    cancellation: CancellationInput | None = Body(default=None),
):
    """Cancela um agendamento; o corpo é opcional."""
    moment_text = cancellation.momento if cancellation is not None else None
    return appointment_service.cancel_appointment(connection, appointment_id, moment_text)


@router.post(
    "/{appointment_id}/atendimento",
    response_model=TreatmentOutput,
    status_code=status.HTTP_201_CREATED,
)
def register_treatment(
    appointment_id: int, data: TreatmentInput, connection: ConnectionDependency
):
    """Registra o atendimento de um agendamento e gera a fatura."""
    return treatment_service.register_treatment(connection, appointment_id, data)
