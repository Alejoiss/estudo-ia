"""Schemas de atendimentos."""

from pydantic import BaseModel

from vetclinic.validation import PositiveInteger, StrictInteger


class UsedProduct(BaseModel):
    """Produto consumido durante um atendimento."""

    produto_id: StrictInteger
    quantidade: PositiveInteger


class TreatmentInput(BaseModel):
    """Corpo de registro de um atendimento (as anotações podem ser vazias)."""

    anotacoes: str
    produtos: list[UsedProduct] = []


class TreatmentOutput(BaseModel):
    """Atendimento retornado pela API."""

    id: int
    agendamento_id: int
    anotacoes: str
    produtos: list[UsedProduct]
    fatura_id: int
