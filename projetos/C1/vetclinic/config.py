"""Configuração da aplicação e constantes de negócio compartilhadas."""

import os
from dataclasses import dataclass

DATABASE_PATH_ENVIRONMENT_VARIABLE = "DB_PATH"
DEFAULT_DATABASE_PATH = "vetclinic.db"

# Tempo máximo (ms) que uma conexão aguarda outra liberar o lock de escrita.
SQLITE_BUSY_TIMEOUT_MILLISECONDS = 5000

# Formatos de data e hora expostos pela API (sem fuso e, no horário, sem segundos).
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
DATETIME_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$"

# Valor fixo da consulta cobrado em toda fatura de atendimento.
CONSULTATION_DESCRIPTION = "Consulta"
CONSULTATION_PRICE_IN_CENTS = 15000


@dataclass(frozen=True)
class Settings:
    """Configurações de execução lidas do ambiente."""

    database_path: str


def load_settings() -> Settings:
    """Lê as configurações do ambiente a cada chamada (permite trocar `DB_PATH` em testes)."""
    database_path = os.environ.get(
        DATABASE_PATH_ENVIRONMENT_VARIABLE, DEFAULT_DATABASE_PATH
    )
    return Settings(database_path=database_path)
