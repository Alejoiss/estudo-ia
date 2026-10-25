"""Regras de negócio de agendamentos."""

import sqlite3
from datetime import datetime, time, timedelta

from vetclinic.database import transaction
from vetclinic.errors import InvalidDataError, ResourceNotFoundError, StateConflictError
from vetclinic.repositories import Row
from vetclinic.repositories import agendamentos as appointment_repository
from vetclinic.schemas.agendamentos import AppointmentInput
from vetclinic.services.pets import get_pet_or_raise
from vetclinic.services.veterinarios import get_veterinarian_or_raise
from vetclinic.validation import format_datetime, parse_datetime_text

STATUS_SCHEDULED = "agendado"
STATUS_COMPLETED = "concluido"
STATUS_CANCELLED = "cancelado"
STATUS_LATE_CANCELLED = "cancelado_tardio"

# Estados que ocupam a agenda do veterinário; cancelamentos liberam o horário.
SLOT_BLOCKING_STATUSES = (STATUS_SCHEDULED, STATUS_COMPLETED)

DURATION_STEP_MINUTES = 15
MINIMUM_DURATION_MINUTES = 15
MAXIMUM_DURATION_MINUTES = 120

# Cancelar com menos antecedência que isto é considerado cancelamento tardio.
LATE_CANCELLATION_THRESHOLD = timedelta(hours=24)

# Expediente por dia da semana (`datetime.weekday()`: segunda=0 ... domingo=6).
# Dias ausentes do mapa estão fechados.
SATURDAY = 5
BUSINESS_HOURS_BY_WEEKDAY: dict[int, tuple[time, time]] = {
    **{weekday: (time(8, 0), time(18, 0)) for weekday in range(5)},
    SATURDAY: (time(8, 0), time(12, 0)),
}

APPOINTMENT_NOT_FOUND_MESSAGE = "Agendamento não encontrado"
INVALID_DURATION_MESSAGE = (
    f"A duração deve ser múltiplo de {DURATION_STEP_MINUTES} minutos, "
    f"entre {MINIMUM_DURATION_MINUTES} e {MAXIMUM_DURATION_MINUTES}"
)
START_IN_PAST_MESSAGE = "O início deve ser posterior ao momento atual"
OUTSIDE_BUSINESS_HOURS_MESSAGE = "O agendamento deve estar dentro do horário de funcionamento"
SCHEDULE_CONFLICT_MESSAGE = "O veterinário já possui agendamento neste horário"
NOT_SCHEDULED_MESSAGE = "Apenas agendamentos com status 'agendado' permitem esta operação"


def get_appointment_or_raise(connection: sqlite3.Connection, appointment_id: int) -> Row:
    """Devolve o agendamento ou levanta `ResourceNotFoundError`."""
    appointment = appointment_repository.find_appointment_by_id(connection, appointment_id)
    if appointment is None:
        raise ResourceNotFoundError(APPOINTMENT_NOT_FOUND_MESSAGE)
    return appointment


def require_scheduled(appointment: Row) -> None:
    """Garante que o agendamento ainda está no estado `agendado`."""
    if appointment["status"] != STATUS_SCHEDULED:
        raise StateConflictError(NOT_SCHEDULED_MESSAGE)


def _validate_duration(duration_minutes: int) -> None:
    is_in_range = MINIMUM_DURATION_MINUTES <= duration_minutes <= MAXIMUM_DURATION_MINUTES
    if not is_in_range or duration_minutes % DURATION_STEP_MINUTES != 0:
        raise InvalidDataError(INVALID_DURATION_MESSAGE)


def _validate_start_is_in_future(start: datetime) -> None:
    if start <= datetime.now():
        raise InvalidDataError(START_IN_PAST_MESSAGE)


def _validate_within_business_hours(start: datetime, end: datetime) -> None:
    """Exige que `[start, end]` caiba inteiro no expediente do mesmo dia."""
    business_hours = BUSINESS_HOURS_BY_WEEKDAY.get(start.weekday())
    if business_hours is None or end.date() != start.date():
        raise InvalidDataError(OUTSIDE_BUSINESS_HOURS_MESSAGE)
    opening_time, closing_time = business_hours
    if start.time() < opening_time or end.time() > closing_time:
        raise InvalidDataError(OUTSIDE_BUSINESS_HOURS_MESSAGE)


def create_appointment(connection: sqlite3.Connection, data: AppointmentInput) -> Row:
    """Cria um agendamento aplicando as regras na ordem definida pela especificação."""
    get_pet_or_raise(connection, data.pet_id)
    get_veterinarian_or_raise(connection, data.veterinario_id)
    _validate_duration(data.duracao_minutos)

    start = parse_datetime_text(data.inicio)
    end = start + timedelta(minutes=data.duracao_minutos)
    _validate_start_is_in_future(start)
    _validate_within_business_hours(start, end)

    start_text, end_text = format_datetime(start), format_datetime(end)
    # Verificação de conflito e inserção na mesma transação: evita dupla reserva.
    with transaction(connection):
        if appointment_repository.exists_overlapping_appointment(
            connection, data.veterinario_id, start_text, end_text, SLOT_BLOCKING_STATUSES
        ):
            raise StateConflictError(SCHEDULE_CONFLICT_MESSAGE)
        appointment_id = appointment_repository.insert_appointment(
            connection,
            data.pet_id,
            data.veterinario_id,
            start_text,
            end_text,
            data.duracao_minutos,
            STATUS_SCHEDULED,
        )
    return get_appointment_or_raise(connection, appointment_id)


def list_appointments(
    connection: sqlite3.Connection, veterinarian_id: int | None, date_text: str | None
) -> list[Row]:
    """Lista agendamentos filtrados por veterinário e/ou dia."""
    return appointment_repository.list_appointments(connection, veterinarian_id, date_text)


def cancel_appointment(
    connection: sqlite3.Connection, appointment_id: int, cancellation_moment_text: str | None
) -> Row:
    """Cancela um agendamento, classificando como tardio se faltar menos de 24 horas."""
    cancellation_moment = (
        parse_datetime_text(cancellation_moment_text)
        if cancellation_moment_text is not None
        else datetime.now()
    )
    with transaction(connection):
        appointment = get_appointment_or_raise(connection, appointment_id)
        require_scheduled(appointment)
        time_until_start = parse_datetime_text(appointment["inicio"]) - cancellation_moment
        is_late = time_until_start < LATE_CANCELLATION_THRESHOLD
        appointment_repository.update_appointment_status(
            connection,
            appointment_id,
            STATUS_LATE_CANCELLED if is_late else STATUS_CANCELLED,
        )
    return get_appointment_or_raise(connection, appointment_id)
