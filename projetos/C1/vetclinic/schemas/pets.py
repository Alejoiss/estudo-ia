"""Schemas de pets."""

from typing import Literal

from pydantic import BaseModel

from vetclinic.validation import NonBlankText, PastOrPresentDateText, StrictInteger

Species = Literal["cao", "gato", "outro"]


class PetInput(BaseModel):
    """Corpo de criação e de substituição de um pet."""

    nome: NonBlankText
    especie: Species
    tutor_id: StrictInteger
    data_nascimento: PastOrPresentDateText | None = None


class PetOutput(PetInput):
    """Pet retornado pela API."""

    id: int
