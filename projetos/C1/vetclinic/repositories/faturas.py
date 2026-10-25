"""Persistência de faturas e seus itens."""

import sqlite3

from vetclinic.repositories import Row

INVOICE_ITEM_COLUMNS = "descricao, quantidade, valor_unitario_centavos"


def insert_invoice(
    connection: sqlite3.Connection,
    tutor_id: int,
    treatment_id: int | None,
    status: str,
    items: list[Row],
) -> int:
    """Insere uma fatura com seus itens iniciais e devolve o id gerado."""
    cursor = connection.execute(
        "INSERT INTO faturas (tutor_id, atendimento_id, status) VALUES (?, ?, ?)",
        (tutor_id, treatment_id, status),
    )
    invoice_id = int(cursor.lastrowid)
    for item in items:
        insert_invoice_item(connection, invoice_id, item)
    return invoice_id


def insert_invoice_item(connection: sqlite3.Connection, invoice_id: int, item: Row) -> None:
    """Acrescenta um item (descrição, quantidade, valor unitário) a uma fatura."""
    connection.execute(
        f"INSERT INTO fatura_itens (fatura_id, {INVOICE_ITEM_COLUMNS}) VALUES (?, ?, ?, ?)",
        (
            invoice_id,
            item["descricao"],
            item["quantidade"],
            item["valor_unitario_centavos"],
        ),
    )


def _load_invoice_items(connection: sqlite3.Connection, invoice_id: int) -> list[Row]:
    rows = connection.execute(
        f"SELECT {INVOICE_ITEM_COLUMNS} FROM fatura_itens WHERE fatura_id = ? ORDER BY id",
        (invoice_id,),
    )
    return [dict(row) for row in rows]


def _row_to_invoice(connection: sqlite3.Connection, row: sqlite3.Row) -> Row:
    invoice = dict(row)
    invoice["itens"] = _load_invoice_items(connection, invoice["id"])
    return invoice


def find_invoice_by_id(connection: sqlite3.Connection, invoice_id: int) -> Row | None:
    """Busca uma fatura pelo id, com seus itens (sem totais calculados)."""
    row = connection.execute("SELECT * FROM faturas WHERE id = ?", (invoice_id,)).fetchone()
    return None if row is None else _row_to_invoice(connection, row)


def list_invoices_of_tutor(connection: sqlite3.Connection, tutor_id: int) -> list[Row]:
    """Lista as faturas de um tutor por id crescente."""
    rows = connection.execute(
        "SELECT * FROM faturas WHERE tutor_id = ? ORDER BY id", (tutor_id,)
    ).fetchall()
    return [_row_to_invoice(connection, row) for row in rows]


def update_invoice_status(connection: sqlite3.Connection, invoice_id: int, status: str) -> None:
    """Altera o status de uma fatura."""
    connection.execute("UPDATE faturas SET status = ? WHERE id = ?", (status, invoice_id))


def find_invoice_id_of_treatment(connection: sqlite3.Connection, treatment_id: int) -> int | None:
    """Devolve o id da fatura gerada por um atendimento, se existir."""
    row = connection.execute(
        "SELECT id FROM faturas WHERE atendimento_id = ?", (treatment_id,)
    ).fetchone()
    return None if row is None else int(row["id"])
