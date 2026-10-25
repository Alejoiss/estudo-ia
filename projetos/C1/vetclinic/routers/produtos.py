"""Rotas de produtos."""

from fastapi import APIRouter, status

from vetclinic.routers import ConnectionDependency
from vetclinic.schemas.produtos import ProductInput, ProductOutput, StockEntryInput
from vetclinic.services import produtos as product_service

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.post("", response_model=ProductOutput, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductInput, connection: ConnectionDependency):
    """Cadastra um produto."""
    return product_service.create_product(connection, data)


@router.get("", response_model=list[ProductOutput])
def list_products(connection: ConnectionDependency):
    """Lista os produtos."""
    return product_service.list_products(connection)


@router.get("/{product_id}", response_model=ProductOutput)
def get_product(product_id: int, connection: ConnectionDependency):
    """Consulta um produto."""
    return product_service.get_product_or_raise(connection, product_id)


@router.post("/{product_id}/entrada", response_model=ProductOutput)
def register_stock_entry(
    product_id: int, data: StockEntryInput, connection: ConnectionDependency
):
    """Registra entrada de estoque."""
    return product_service.register_stock_entry(connection, product_id, data.quantidade)
