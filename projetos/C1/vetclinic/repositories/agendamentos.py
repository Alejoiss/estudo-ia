"""Persistência de agendamentos."""

import sqlite3

from vetclinic.repositories import Row, row_to_dict

# Tamanho do prefixo "YYYY-MM-DD" dentro do texto "YYYY-MM-DDTHH:MM".
DATE_PREFIX_LENGTH = 10


def insert_appointment(
    connection: sqlite3.Connection,
    pet_id: int,
    veterinarian_id: int,
    start_text: str,
    end_text: str,
    duration_minutes: int,
    status: str,
) -> int:
    """Insere um agendamento e devolve o id gerado."""
    cursor = connection.execute(
        "INSERT INTO agendamentos"
        " (pet_id, veterinario_id, inicio, fim, duracao_minutos, status)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (pet_id, veterinarian_id, start_text, end_text, duration_minutes, status),
    )
    return int(cursor.lastrowid)


def find_appointment_by_id(connection: sqlite3.Connection, appointment_id: int) -> Row | None:
    """Busca um agendamento pelo id."""
    return row_to_dict(
        connection.execute(
            "SELECT * FROM agendamentos WHERE id = ?", (appointment_id,)
        ).fetchone()
    )


def list_appointments(
    connection: sqlite3.Connection, veterinarian_id: int | None, date_text: str | None
) -> list[Row]:
    """Lista agendamentos por início crescente, com filtros opcionais e combináveis."""
    conditions: list[str] = []
    parameters: list[object] = []
    if veterinarian_id is not None:
        conditions.append("veterinario_id = ?")
        parameters.append(veterinarian_id)
    if date_text is not None:
        conditions.append(f"substr(inicio, 1, {DATE_PREFIX_LENGTH}) = ?")
        parameters.append(date_text)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    rows = connection.execute(
        f"SELECT * FROM agendamentos {where_clause} ORDER BY inicio, id", parameters
    )
    return [dict(row) for row in rows]


def exists_overlapping_appointment(
    connection: sqlite3.Connection,
    veterinarian_id: int,
    start_text: str,
    end_text: str,
    blocking_statuses: tuple[str, ...],
) -> bool:
    """Indica se há agendamento bloqueante que se sobreponha a `[start, end)`.

    Os textos ISO de mesmo formato são comparáveis lexicograficamente, e a condição
    `inicio < novo_fim AND fim > novo_inicio` trata os intervalos como semiabertos.
    """
    placeholders = ", ".join("?" for _ in blocking_statuses)
    row = connection.execute(
        f"SELECT 1 FROM agendamentos WHERE veterinario_id = ? AND status IN ({placeholders})"
        " AND inicio < ? AND fim > ? LIMIT 1",
        (veterinarian_id, *blocking_statuses, end_text, start_text),
    ).fetchone()
    return row is not None


def count_appointments_of_pet(connection: sqlite3.Connection, pet_id: int) -> int:
    """Conta os agendamentos de um pet, em qualquer status."""
    return connection.execute(
        "SELECT COUNT(*) FROM agendamentos WHERE pet_id = ?", (pet_id,)
    ).fetchone()[0]


def update_appointment_status(
    connection: sqlite3.Connection, appointment_id: int, status: str
) -> None:
    """Altera o status de um agendamento."""
    connection.execute(
        "UPDATE agendamentos SET status = ? WHERE id = ?", (status, appointment_id)
    )
