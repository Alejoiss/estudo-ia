"""Repositórios: único ponto de contato com o SQL; devolvem dicionários simples."""

import sqlite3
from typing import Any

Row = dict[str, Any]


def row_to_dict(row: sqlite3.Row | None) -> Row | None:
    """Converte uma linha do SQLite em dicionário, preservando `None` para 'não achado'."""
    return None if row is None else dict(row)
