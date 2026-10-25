"""Schemas de faturas."""

from typing import Literal

from pydantic import BaseModel

from vetclinic.validation import NonBlankText, NonNegativeInteger, PositiveInteger

InvoiceStatus = Literal["aberta", "paga"]


class InvoiceItemInput(BaseModel):
    """Corpo de inclusão de um item avulso em uma fatura aberta."""

    descricao: NonBlankText
    quantidade: PositiveInteger
    valor_unitario_centavos: NonNegativeInteger


class InvoiceItemOutput(BaseModel):
    """Item de fatura retornado pela API."""

    descricao: str
    quantidade: int
    valor_unitario_centavos: int
    total_centavos: int


class InvoiceOutput(BaseModel):
    """Fatura retornada pela API."""

    id: int
    tutor_id: int
    atendimento_id: int | None
    status: InvoiceStatus
    itens: list[InvoiceItemOutput]
    total_centavos: int
