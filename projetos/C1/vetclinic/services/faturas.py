"""Regras de negócio de faturas."""

import sqlite3

from vetclinic.config import CONSULTATION_DESCRIPTION, CONSULTATION_PRICE_IN_CENTS
from vetclinic.database import transaction
from vetclinic.errors import ResourceNotFoundError, StateConflictError
from vetclinic.repositories import Row
from vetclinic.repositories import faturas as invoice_repository
from vetclinic.schemas.faturas import InvoiceItemInput

INVOICE_STATUS_OPEN = "aberta"
INVOICE_STATUS_PAID = "paga"

INVOICE_NOT_FOUND_MESSAGE = "Fatura não encontrada"
INVOICE_ALREADY_PAID_MESSAGE = "Fatura já está paga"


def build_invoice_item(description: str, quantity: int, unit_price_in_cents: int) -> Row:
    """Monta um item de fatura no formato aceito pelo repositório."""
    return {
        "descricao": description,
        "quantidade": quantity,
        "valor_unitario_centavos": unit_price_in_cents,
    }


def build_consultation_item() -> Row:
    """Item fixo de consulta presente em toda fatura de atendimento."""
    return build_invoice_item(CONSULTATION_DESCRIPTION, 1, CONSULTATION_PRICE_IN_CENTS)


def add_totals_to_invoice(invoice: Row) -> Row:
    """Devolve a fatura com o total de cada item e o total geral calculados."""
    items_with_totals = [
        {**item, "total_centavos": item["quantidade"] * item["valor_unitario_centavos"]}
        for item in invoice["itens"]
    ]
    return {
        **invoice,
        "itens": items_with_totals,
        "total_centavos": sum(item["total_centavos"] for item in items_with_totals),
    }


def create_invoice_for_treatment(
    connection: sqlite3.Connection, tutor_id: int, treatment_id: int, items: list[Row]
) -> int:
    """Cria a fatura aberta de um atendimento. Deve rodar dentro da transação do chamador."""
    return invoice_repository.insert_invoice(
        connection, tutor_id, treatment_id, INVOICE_STATUS_OPEN, items
    )


def get_invoice(connection: sqlite3.Connection, invoice_id: int) -> Row:
    """Devolve a fatura com totais ou levanta `ResourceNotFoundError`."""
    invoice = invoice_repository.find_invoice_by_id(connection, invoice_id)
    if invoice is None:
        raise ResourceNotFoundError(INVOICE_NOT_FOUND_MESSAGE)
    return add_totals_to_invoice(invoice)


def _require_invoice_open(invoice: Row) -> None:
    if invoice["status"] == INVOICE_STATUS_PAID:
        raise StateConflictError(INVOICE_ALREADY_PAID_MESSAGE)


def add_item_to_invoice(
    connection: sqlite3.Connection, invoice_id: int, data: InvoiceItemInput
) -> Row:
    """Acrescenta um item a uma fatura que ainda esteja aberta."""
    with transaction(connection):
        _require_invoice_open(get_invoice(connection, invoice_id))
        invoice_repository.insert_invoice_item(
            connection,
            invoice_id,
            build_invoice_item(data.descricao, data.quantidade, data.valor_unitario_centavos),
        )
    return get_invoice(connection, invoice_id)


def pay_invoice(connection: sqlite3.Connection, invoice_id: int) -> Row:
    """Marca como paga uma fatura que ainda esteja aberta."""
    with transaction(connection):
        _require_invoice_open(get_invoice(connection, invoice_id))
        invoice_repository.update_invoice_status(connection, invoice_id, INVOICE_STATUS_PAID)
    return get_invoice(connection, invoice_id)
