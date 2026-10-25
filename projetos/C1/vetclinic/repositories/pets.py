"""Persistência de pets."""

import sqlite3

from vetclinic.repositories import Row, row_to_dict


def insert_pet(
    connection: sqlite3.Connection,
    nome: str,
    especie: str,
    tutor_id: int,
    data_nascimento: str | None,
) -> int:
    """Insere um pet e devolve o id gerado."""
    cursor = connection.execute(
        "INSERT INTO pets (nome, especie, tutor_id, data_nascimento) VALUES (?, ?, ?, ?)",
        (nome, especie, tutor_id, data_nascimento),
    )
    return int(cursor.lastrowid)


def find_pet_by_id(connection: sqlite3.Connection, pet_id: int) -> Row | None:
    """Busca um pet pelo id."""
    return row_to_dict(
        connection.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()
    )


def list_pets_of_tutor(connection: sqlite3.Connection, tutor_id: int) -> list[Row]:
    """Lista os pets de um tutor por id crescente."""
    rows = connection.execute("SELECT * FROM pets WHERE tutor_id = ? ORDER BY id", (tutor_id,))
    return [dict(row) for row in rows]


def count_pets_of_tutor(connection: sqlite3.Connection, tutor_id: int) -> int:
    """Conta os pets de um tutor."""
    return connection.execute(
        "SELECT COUNT(*) FROM pets WHERE tutor_id = ?", (tutor_id,)
    ).fetchone()[0]


def update_pet(
    connection: sqlite3.Connection,
    pet_id: int,
    nome: str,
    especie: str,
    tutor_id: int,
    data_nascimento: str | None,
) -> None:
    """Substitui os dados de um pet."""
    connection.execute(
        "UPDATE pets SET nome = ?, especie = ?, tutor_id = ?, data_nascimento = ? WHERE id = ?",
        (nome, especie, tutor_id, data_nascimento, pet_id),
    )


def delete_pet(connection: sqlite3.Connection, pet_id: int) -> None:
    """Remove um pet."""
    connection.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
