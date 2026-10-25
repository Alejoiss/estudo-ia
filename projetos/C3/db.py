import os
import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS tutores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT NOT NULL, telefone TEXT);
CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, especie TEXT NOT NULL,
    tutor_id INTEGER NOT NULL REFERENCES tutores(id), data_nascimento TEXT);
CREATE TABLE IF NOT EXISTS veterinarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, crmv TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
    preco_centavos INTEGER NOT NULL, estoque INTEGER NOT NULL, estoque_minimo INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS agendamentos (id INTEGER PRIMARY KEY AUTOINCREMENT, pet_id INTEGER NOT NULL REFERENCES pets(id),
    veterinario_id INTEGER NOT NULL REFERENCES veterinarios(id), inicio TEXT NOT NULL, fim TEXT NOT NULL,
    duracao_minutos INTEGER NOT NULL, status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS atendimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, agendamento_id INTEGER NOT NULL REFERENCES agendamentos(id),
    anotacoes TEXT NOT NULL, produtos_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS faturas (id INTEGER PRIMARY KEY AUTOINCREMENT, tutor_id INTEGER NOT NULL REFERENCES tutores(id),
    atendimento_id INTEGER, status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fatura_itens (id INTEGER PRIMARY KEY AUTOINCREMENT, fatura_id INTEGER NOT NULL REFERENCES faturas(id),
    descricao TEXT NOT NULL, quantidade INTEGER NOT NULL, valor_unitario_centavos INTEGER NOT NULL);
"""


@contextmanager
def db():
    """Conexão por uso; commit ao sair, rollback se houver exceção."""
    c = sqlite3.connect(os.environ.get("DB_PATH", "vetclinic.db"), timeout=30)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    except BaseException:
        c.rollback()
        raise
    finally:
        c.close()


def iniciar():
    with db() as c:
        c.executescript(SCHEMA)


def um(c, sql, *args):
    """Primeira linha como dict, ou None."""
    r = c.execute(sql, args).fetchone()
    return dict(r) if r else None


def todos(c, sql, *args):
    return [dict(r) for r in c.execute(sql, args).fetchall()]


def inserir(c, sql, *args):
    """Executa INSERT e devolve o id criado."""
    return c.execute(sql, args).lastrowid
