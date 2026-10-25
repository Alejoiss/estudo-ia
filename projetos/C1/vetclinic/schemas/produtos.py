"""Schemas de produtos."""

from pydantic import BaseModel

from vetclinic.validation import NonBlankText, NonNegativeInteger, PositiveInteger


class ProductInput(BaseModel):
    """Corpo de criação de um produto."""

    nome: NonBlankText
    preco_centavos: NonNegativeInteger
    estoque: NonNegativeInteger
    estoque_minimo: NonNegativeInteger


class ProductOutput(ProductInput):
    """Produto retornado pela API."""

    id: int


class StockEntryInput(BaseModel):
    """Corpo de uma entrada de estoque."""

    quantidade: PositiveInteger
