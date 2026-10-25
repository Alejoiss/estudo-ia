"""Schemas de agendamentos."""

from typing import Literal

from pydantic import BaseModel

from vetclinic.validation import DateTimeText, StrictInteger

DEFAULT_APPOINTMENT_DURATION_MINUTES = 30

AppointmentStatus = Literal["agendado", "concluido", "cancelado", "cancelado_tardio"]


class AppointmentInput(BaseModel):
    """Corpo de criação de um agendamento.

    A duração é validada pelo serviço (e não aqui) para respeitar a ordem das regras
    da especificação: existência de pet/veterinário vem antes da validação de duração.
    """

    pet_id: StrictInteger
    veterinario_id: StrictInteger
    inicio: DateTimeText
    duracao_minutos: StrictInteger = DEFAULT_APPOINTMENT_DURATION_MINUTES


class AppointmentOutput(BaseModel):
    """Agendamento retornado pela API."""

    id: int
    pet_id: int
    veterinario_id: int
    inicio: str
    fim: str
    duracao_minutos: int
    status: AppointmentStatus


class CancellationInput(BaseModel):
    """Corpo opcional do cancelamento; `momento` permite testes determinísticos."""

    momento: DateTimeText | None = None
