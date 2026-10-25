"""Persistência de veterinários."""

import sqlite3

from vetclinic.repositories import Row, row_to_dict


def insert_veterinarian(connection: sqlite3.Connection, nome: str, crmv: str) -> int:
    """Insere um veterinário e devolve o id gerado.

    Levanta `sqlite3.IntegrityError` se o CRMV já existir (restrição UNIQUE).
    """
    cursor = connection.execute(
        "INSERT INTO veterinarios (nome, crmv) VALUES (?, ?)", (nome, crmv)
    )
    return int(cursor.lastrowid)


def find_veterinarian_by_id(connection: sqlite3.Connection, veterinarian_id: int) -> Row | None:
    """Busca um veterinário pelo id."""
    return row_to_dict(
        connection.execute(
            "SELECT * FROM veterinarios WHERE id = ?", (veterinarian_id,)
        ).fetchone()
    )


def find_veterinarian_by_crmv(connection: sqlite3.Connection, crmv: str) -> Row | None:
    """Busca um veterinário pelo CRMV."""
    return row_to_dict(
        connection.execute("SELECT * FROM veterinarios WHERE crmv = ?", (crmv,)).fetchone()
    )


def list_veterinarians(connection: sqlite3.Connection) -> list[Row]:
    """Lista todos os veterinários por id crescente."""
    return [dict(row) for row in connection.execute("SELECT * FROM veterinarios ORDER BY id")]
