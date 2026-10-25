"""Regras de negócio de produtos e estoque."""

import sqlite3

from vetclinic.database import transaction
from vetclinic.errors import ResourceNotFoundError
from vetclinic.repositories import Row
from vetclinic.repositories import produtos as product_repository
from vetclinic.schemas.produtos import ProductInput

PRODUCT_NOT_FOUND_MESSAGE = "Produto não encontrado"


def get_product_or_raise(connection: sqlite3.Connection, product_id: int) -> Row:
    """Devolve o produto ou levanta `ResourceNotFoundError`."""
    product = product_repository.find_product_by_id(connection, product_id)
    if product is None:
        raise ResourceNotFoundError(PRODUCT_NOT_FOUND_MESSAGE)
    return product


def create_product(connection: sqlite3.Connection, data: ProductInput) -> Row:
    """Cadastra um produto."""
    product_id = product_repository.insert_product(
        connection, data.nome, data.preco_centavos, data.estoque, data.estoque_minimo
    )
    return get_product_or_raise(connection, product_id)


def list_products(connection: sqlite3.Connection) -> list[Row]:
    """Lista os produtos."""
    return product_repository.list_products(connection)


def register_stock_entry(connection: sqlite3.Connection, product_id: int, quantity: int) -> Row:
    """Soma `quantity` ao estoque de um produto existente."""
    with transaction(connection):
        get_product_or_raise(connection, product_id)
        product_repository.add_to_stock(connection, product_id, quantity)
    return get_product_or_raise(connection, product_id)
