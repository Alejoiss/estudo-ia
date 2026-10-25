"""Schemas de tutores."""

from pydantic import BaseModel

from vetclinic.validation import EmailText, NonBlankText


class TutorInput(BaseModel):
    """Corpo de criação e de substituição de um tutor."""

    nome: NonBlankText
    email: EmailText
    telefone: str | None = None


class TutorOutput(TutorInput):
    """Tutor retornado pela API."""

    id: int
