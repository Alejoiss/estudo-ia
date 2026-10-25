"""Persistência de atendimentos e dos produtos usados neles."""

import sqlite3

from vetclinic.repositories import Row, row_to_dict


def insert_treatment(
    connection: sqlite3.Connection,
    appointment_id: int,
    notes: str,
    used_products: list[tuple[int, int]],
) -> int:
    """Insere um atendimento com seus produtos `(produto_id, quantidade)`; devolve o id."""
    cursor = connection.execute(
        "INSERT INTO atendimentos (agendamento_id, anotacoes) VALUES (?, ?)",
        (appointment_id, notes),
    )
    treatment_id = int(cursor.lastrowid)
    connection.executemany(
        "INSERT INTO atendimento_produtos (atendimento_id, produto_id, quantidade)"
        " VALUES (?, ?, ?)",
        [(treatment_id, product_id, quantity) for product_id, quantity in used_products],
    )
    return treatment_id


def find_treatment_by_id(connection: sqlite3.Connection, treatment_id: int) -> Row | None:
    """Busca um atendimento pelo id, já com a lista de produtos usados."""
    treatment = row_to_dict(
        connection.execute(
            "SELECT * FROM atendimentos WHERE id = ?", (treatment_id,)
        ).fetchone()
    )
    if treatment is None:
        return None
    product_rows = connection.execute(
        "SELECT produto_id, quantidade FROM atendimento_produtos"
        " WHERE atendimento_id = ? ORDER BY id",
        (treatment_id,),
    )
    treatment["produtos"] = [dict(row) for row in product_rows]
    return treatment
