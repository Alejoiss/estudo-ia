"""Persistência de tutores."""

import sqlite3

from vetclinic.repositories import Row, row_to_dict


def insert_tutor(connection: sqlite3.Connection, nome: str, email: str, telefone: str | None) -> int:
    """Insere um tutor e devolve o id gerado."""
    cursor = connection.execute(
        "INSERT INTO tutores (nome, email, telefone) VALUES (?, ?, ?)",
        (nome, email, telefone),
    )
    return int(cursor.lastrowid)


def find_tutor_by_id(connection: sqlite3.Connection, tutor_id: int) -> Row | None:
    """Busca um tutor pelo id."""
    return row_to_dict(
        connection.execute("SELECT * FROM tutores WHERE id = ?", (tutor_id,)).fetchone()
    )


def list_tutors(connection: sqlite3.Connection) -> list[Row]:
    """Lista todos os tutores por id crescente."""
    return [dict(row) for row in connection.execute("SELECT * FROM tutores ORDER BY id")]


def update_tutor(
    connection: sqlite3.Connection, tutor_id: int, nome: str, email: str, telefone: str | None
) -> None:
    """Substitui os dados de um tutor."""
    connection.execute(
        "UPDATE tutores SET nome = ?, email = ?, telefone = ? WHERE id = ?",
        (nome, email, telefone, tutor_id),
    )


def delete_tutor(connection: sqlite3.Connection, tutor_id: int) -> None:
    """Remove um tutor."""
    connection.execute("DELETE FROM tutores WHERE id = ?", (tutor_id,))
