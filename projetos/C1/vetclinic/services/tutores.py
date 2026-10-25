"""Regras de negócio de tutores."""

import sqlite3

from vetclinic.errors import ResourceNotFoundError, StateConflictError
from vetclinic.repositories import Row, faturas as invoice_repository
from vetclinic.repositories import pets as pet_repository
from vetclinic.repositories import tutores as tutor_repository
from vetclinic.schemas.tutores import TutorInput
from vetclinic.services.faturas import add_totals_to_invoice

TUTOR_NOT_FOUND_MESSAGE = "Tutor não encontrado"
TUTOR_HAS_PETS_MESSAGE = "Tutor possui pets e não pode ser excluído"


def get_tutor_or_raise(connection: sqlite3.Connection, tutor_id: int) -> Row:
    """Devolve o tutor ou levanta `ResourceNotFoundError`."""
    tutor = tutor_repository.find_tutor_by_id(connection, tutor_id)
    if tutor is None:
        raise ResourceNotFoundError(TUTOR_NOT_FOUND_MESSAGE)
    return tutor


def create_tutor(connection: sqlite3.Connection, data: TutorInput) -> Row:
    """Cadastra um tutor."""
    tutor_id = tutor_repository.insert_tutor(connection, data.nome, data.email, data.telefone)
    return get_tutor_or_raise(connection, tutor_id)


def list_tutors(connection: sqlite3.Connection) -> list[Row]:
    """Lista os tutores."""
    return tutor_repository.list_tutors(connection)


def replace_tutor(connection: sqlite3.Connection, tutor_id: int, data: TutorInput) -> Row:
    """Substitui os dados de um tutor existente."""
    get_tutor_or_raise(connection, tutor_id)
    tutor_repository.update_tutor(connection, tutor_id, data.nome, data.email, data.telefone)
    return get_tutor_or_raise(connection, tutor_id)


def delete_tutor(connection: sqlite3.Connection, tutor_id: int) -> None:
    """Exclui um tutor que não possua pets."""
    get_tutor_or_raise(connection, tutor_id)
    if pet_repository.count_pets_of_tutor(connection, tutor_id) > 0:
        raise StateConflictError(TUTOR_HAS_PETS_MESSAGE)
    tutor_repository.delete_tutor(connection, tutor_id)


def list_pets_of_tutor(connection: sqlite3.Connection, tutor_id: int) -> list[Row]:
    """Lista os pets de um tutor existente."""
    get_tutor_or_raise(connection, tutor_id)
    return pet_repository.list_pets_of_tutor(connection, tutor_id)


def list_invoices_of_tutor(connection: sqlite3.Connection, tutor_id: int) -> list[Row]:
    """Lista as faturas (com totais) de um tutor existente."""
    get_tutor_or_raise(connection, tutor_id)
    invoices = invoice_repository.list_invoices_of_tutor(connection, tutor_id)
    return [add_totals_to_invoice(invoice) for invoice in invoices]
