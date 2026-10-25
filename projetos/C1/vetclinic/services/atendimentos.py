"""Regras de negócio de atendimentos."""

import sqlite3
from collections import defaultdict

from vetclinic.database import transaction
from vetclinic.errors import ResourceNotFoundError, StateConflictError
from vetclinic.repositories import Row
from vetclinic.repositories import agendamentos as appointment_repository
from vetclinic.repositories import atendimentos as treatment_repository
from vetclinic.repositories import faturas as invoice_repository
from vetclinic.repositories import produtos as product_repository
from vetclinic.schemas.atendimentos import TreatmentInput, UsedProduct
from vetclinic.services.agendamentos import (
    STATUS_COMPLETED,
    get_appointment_or_raise,
    require_scheduled,
)
from vetclinic.services.faturas import (
    build_consultation_item,
    build_invoice_item,
    create_invoice_for_treatment,
)
from vetclinic.services.pets import get_pet_or_raise
from vetclinic.services.produtos import get_product_or_raise

TREATMENT_NOT_FOUND_MESSAGE = "Atendimento não encontrado"
INSUFFICIENT_STOCK_MESSAGE = "Estoque insuficiente para o produto '{product_name}'"


def _load_products_or_raise(
    connection: sqlite3.Connection, used_products: list[UsedProduct]
) -> dict[int, Row]:
    """Carrega cada produto distinto citado; qualquer id inexistente resulta em 404."""
    return {
        used.produto_id: get_product_or_raise(connection, used.produto_id)
        for used in used_products
    }


def _require_sufficient_stock(
    used_products: list[UsedProduct], products_by_id: dict[int, Row]
) -> None:
    """Valida o estoque somando as quantidades de um mesmo produto repetido na lista."""
    requested_quantity_by_product: dict[int, int] = defaultdict(int)
    for used in used_products:
        requested_quantity_by_product[used.produto_id] += used.quantidade
    for product_id, requested_quantity in requested_quantity_by_product.items():
        product = products_by_id[product_id]
        if requested_quantity > product["estoque"]:
            raise StateConflictError(
                INSUFFICIENT_STOCK_MESSAGE.format(product_name=product["nome"])
            )


def _build_invoice_items(
    used_products: list[UsedProduct], products_by_id: dict[int, Row]
) -> list[Row]:
    """Consulta primeiro e depois um item por produto, na ordem enviada, com o preço atual."""
    product_items = [
        build_invoice_item(
            products_by_id[used.produto_id]["nome"],
            used.quantidade,
            products_by_id[used.produto_id]["preco_centavos"],
        )
        for used in used_products
    ]
    return [build_consultation_item(), *product_items]


def register_treatment(
    connection: sqlite3.Connection, appointment_id: int, data: TreatmentInput
) -> Row:
    """Registra o atendimento, baixa o estoque, conclui o agendamento e gera a fatura.

    Tudo ocorre em uma única transação: qualquer falha desfaz todas as alterações.
    A ordem das verificações segue a especificação (404 antes de 409).
    """
    with transaction(connection):
        appointment = get_appointment_or_raise(connection, appointment_id)
        products_by_id = _load_products_or_raise(connection, data.produtos)
        require_scheduled(appointment)
        _require_sufficient_stock(data.produtos, products_by_id)

        for used in data.produtos:
            product_repository.add_to_stock(connection, used.produto_id, -used.quantidade)
        appointment_repository.update_appointment_status(
            connection, appointment_id, STATUS_COMPLETED
        )
        treatment_id = treatment_repository.insert_treatment(
            connection,
            appointment_id,
            data.anotacoes,
            [(used.produto_id, used.quantidade) for used in data.produtos],
        )
        tutor_id = get_pet_or_raise(connection, appointment["pet_id"])["tutor_id"]
        invoice_id = create_invoice_for_treatment(
            connection, tutor_id, treatment_id, _build_invoice_items(data.produtos, products_by_id)
        )
    return get_treatment_with_invoice(connection, treatment_id, invoice_id)


def get_treatment_with_invoice(
    connection: sqlite3.Connection, treatment_id: int, invoice_id: int | None = None
) -> Row:
    """Devolve o atendimento acrescido do id da fatura gerada por ele."""
    treatment = treatment_repository.find_treatment_by_id(connection, treatment_id)
    if treatment is None:
        raise ResourceNotFoundError(TREATMENT_NOT_FOUND_MESSAGE)
    if invoice_id is None:
        invoice_id = invoice_repository.find_invoice_id_of_treatment(connection, treatment_id)
    return {**treatment, "fatura_id": invoice_id}
