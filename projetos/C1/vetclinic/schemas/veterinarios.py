"""Schemas de veterinários."""

from pydantic import BaseModel

from vetclinic.validation import NonBlankText


class VeterinarianInput(BaseModel):
    """Corpo de criação de um veterinário."""

    nome: NonBlankText
    crmv: NonBlankText


class VeterinarianOutput(VeterinarianInput):
    """Veterinário retornado pela API."""

    id: int
