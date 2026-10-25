"""Acesso ao SQLite: conexões, criação do esquema e controle de transações."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from vetclinic.config import SQLITE_BUSY_TIMEOUT_MILLISECONDS, load_settings

DATABASE_SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS tutores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        telefone TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        especie TEXT NOT NULL,
        tutor_id INTEGER NOT NULL REFERENCES tutores(id),
        data_nascimento TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS veterinarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        crmv TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco_centavos INTEGER NOT NULL,
        estoque INTEGER NOT NULL,
        estoque_minimo INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL REFERENCES pets(id),
        veterinario_id INTEGER NOT NULL REFERENCES veterinarios(id),
        inicio TEXT NOT NULL,
        fim TEXT NOT NULL,
        duracao_minutos INTEGER NOT NULL,
        status TEXT NOT NULL
    )
    """,
    # Índice de apoio à verificação de conflito e à listagem por veterinário.
    """
    CREATE INDEX IF NOT EXISTS idx_agendamentos_veterinario_inicio
        ON agendamentos(veterinario_id, inicio)
    """,
    """
    CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agendamento_id INTEGER NOT NULL UNIQUE REFERENCES agendamentos(id),
        anotacoes TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS atendimento_produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        atendimento_id INTEGER NOT NULL REFERENCES atendimentos(id),
        produto_id INTEGER NOT NULL REFERENCES produtos(id),
        quantidade INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS faturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tutor_id INTEGER NOT NULL REFERENCES tutores(id),
        atendimento_id INTEGER REFERENCES atendimentos(id),
        status TEXT NOT NULL
    )
    """,
    # O total da fatura não é armazenado: é sempre derivado dos itens.
    """
    CREATE TABLE IF NOT EXISTS fatura_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fatura_id INTEGER NOT NULL REFERENCES faturas(id),
        descricao TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor_unitario_centavos INTEGER NOT NULL
    )
    """,
)


def open_connection(database_path: str) -> sqlite3.Connection:
    """Abre uma conexão configurada para controle manual de transações.

    `isolation_level=None` desliga o BEGIN implícito do módulo `sqlite3`, de modo que
    `transaction` decide exatamente onde cada transação começa e termina.
    `check_same_thread=False` é necessário porque o FastAPI pode abrir e fechar a
    conexão em threads diferentes do pool.
    """
    connection = sqlite3.connect(
        database_path,
        isolation_level=None,
        check_same_thread=False,
        timeout=SQLITE_BUSY_TIMEOUT_MILLISECONDS / 1000,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_schema(database_path: str) -> None:
    """Cria as tabelas que ainda não existem."""
    connection = open_connection(database_path)
    try:
        for statement in DATABASE_SCHEMA_STATEMENTS:
            connection.execute(statement)
    finally:
        connection.close()


def get_connection() -> Iterator[sqlite3.Connection]:
    """Dependência do FastAPI: uma conexão por requisição, sempre fechada ao final."""
    connection = open_connection(load_settings().database_path)
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def transaction(connection: sqlite3.Connection) -> Iterator[None]:
    """Executa o bloco em uma transação atômica.

    Usa `BEGIN IMMEDIATE` para obter o lock de escrita logo no início: assim, uma
    verificação (ex.: conflito de agenda, estoque) e a escrita que depende dela não
    podem ser intercaladas por outra requisição concorrente.
    """
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    connection.execute("COMMIT")
