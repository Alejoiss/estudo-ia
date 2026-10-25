"""Persistência de produtos."""

import sqlite3

from vetclinic.repositories import Row, row_to_dict


def insert_product(
    connection: sqlite3.Connection,
    nome: str,
    preco_centavos: int,
    estoque: int,
    estoque_minimo: int,
) -> int:
    """Insere um produto e devolve o id gerado."""
    cursor = connection.execute(
        "INSERT INTO produtos (nome, preco_centavos, estoque, estoque_minimo)"
        " VALUES (?, ?, ?, ?)",
        (nome, preco_centavos, estoque, estoque_minimo),
    )
    return int(cursor.lastrowid)


def find_product_by_id(connection: sqlite3.Connection, product_id: int) -> Row | None:
    """Busca um produto pelo id."""
    return row_to_dict(
        connection.execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()
    )


def list_products(connection: sqlite3.Connection) -> list[Row]:
    """Lista todos os produtos por id crescente."""
    return [dict(row) for row in connection.execute("SELECT * FROM produtos ORDER BY id")]


def add_to_stock(connection: sqlite3.Connection, product_id: int, quantity: int) -> None:
    """Soma `quantity` ao estoque (use valor negativo para baixar)."""
    connection.execute(
        "UPDATE produtos SET estoque = estoque + ? WHERE id = ?", (quantity, product_id)
    )
