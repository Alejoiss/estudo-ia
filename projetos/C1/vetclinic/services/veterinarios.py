"""Regras de negócio de veterinários."""

import sqlite3

from vetclinic.database import transaction
from vetclinic.errors import ResourceNotFoundError, StateConflictError
from vetclinic.repositories import Row
from vetclinic.repositories import veterinarios as veterinarian_repository
from vetclinic.schemas.veterinarios import VeterinarianInput

VETERINARIAN_NOT_FOUND_MESSAGE = "Veterinário não encontrado"
DUPLICATE_CRMV_MESSAGE = "Já existe um veterinário com este CRMV"


def get_veterinarian_or_raise(connection: sqlite3.Connection, veterinarian_id: int) -> Row:
    """Devolve o veterinário ou levanta `ResourceNotFoundError`."""
    veterinarian = veterinarian_repository.find_veterinarian_by_id(connection, veterinarian_id)
    if veterinarian is None:
        raise ResourceNotFoundError(VETERINARIAN_NOT_FOUND_MESSAGE)
    return veterinarian


def create_veterinarian(connection: sqlite3.Connection, data: VeterinarianInput) -> Row:
    """Cadastra um veterinário, garantindo CRMV único.

    A checagem e a inserção ocorrem na mesma transação; a restrição UNIQUE do banco
    continua sendo a garantia final contra corridas.
    """
    with transaction(connection):
        if veterinarian_repository.find_veterinarian_by_crmv(connection, data.crmv):
            raise StateConflictError(DUPLICATE_CRMV_MESSAGE)
        veterinarian_id = veterinarian_repository.insert_veterinarian(
            connection, data.nome, data.crmv
        )
    return get_veterinarian_or_raise(connection, veterinarian_id)


def list_veterinarians(connection: sqlite3.Connection) -> list[Row]:
    """Lista os veterinários."""
    return veterinarian_repository.list_veterinarians(connection)
