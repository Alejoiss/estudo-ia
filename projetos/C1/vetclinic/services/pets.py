"""Regras de negócio de pets."""

import sqlite3

from vetclinic.errors import ResourceNotFoundError, StateConflictError
from vetclinic.repositories import Row
from vetclinic.repositories import agendamentos as appointment_repository
from vetclinic.repositories import pets as pet_repository
from vetclinic.schemas.pets import PetInput
from vetclinic.services.tutores import get_tutor_or_raise

PET_NOT_FOUND_MESSAGE = "Pet não encontrado"
PET_HAS_APPOINTMENTS_MESSAGE = "Pet possui agendamentos e não pode ser excluído"


def get_pet_or_raise(connection: sqlite3.Connection, pet_id: int) -> Row:
    """Devolve o pet ou levanta `ResourceNotFoundError`."""
    pet = pet_repository.find_pet_by_id(connection, pet_id)
    if pet is None:
        raise ResourceNotFoundError(PET_NOT_FOUND_MESSAGE)
    return pet


def create_pet(connection: sqlite3.Connection, data: PetInput) -> Row:
    """Cadastra um pet para um tutor existente."""
    get_tutor_or_raise(connection, data.tutor_id)
    pet_id = pet_repository.insert_pet(
        connection, data.nome, data.especie, data.tutor_id, data.data_nascimento
    )
    return get_pet_or_raise(connection, pet_id)


def replace_pet(connection: sqlite3.Connection, pet_id: int, data: PetInput) -> Row:
    """Substitui os dados de um pet existente."""
    get_pet_or_raise(connection, pet_id)
    get_tutor_or_raise(connection, data.tutor_id)
    pet_repository.update_pet(
        connection, pet_id, data.nome, data.especie, data.tutor_id, data.data_nascimento
    )
    return get_pet_or_raise(connection, pet_id)


def delete_pet(connection: sqlite3.Connection, pet_id: int) -> None:
    """Exclui um pet que não possua agendamentos."""
    get_pet_or_raise(connection, pet_id)
    if appointment_repository.count_appointments_of_pet(connection, pet_id) > 0:
        raise StateConflictError(PET_HAS_APPOINTMENTS_MESSAGE)
    pet_repository.delete_pet(connection, pet_id)
