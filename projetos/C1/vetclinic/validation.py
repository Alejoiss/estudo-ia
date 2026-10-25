"""Tipos de validação reutilizáveis pelos schemas de entrada."""

from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, Field, StringConstraints

from vetclinic.config import (
    DATE_FORMAT,
    DATE_PATTERN,
    DATETIME_FORMAT,
    DATETIME_PATTERN,
)


def parse_date_text(text: str) -> date:
    """Converte `YYYY-MM-DD` em `date`; levanta `ValueError` se o formato for inválido."""
    return datetime.strptime(text, DATE_FORMAT).date()


def parse_datetime_text(text: str) -> datetime:
    """Converte `YYYY-MM-DDTHH:MM` em `datetime`; levanta `ValueError` se inválido."""
    return datetime.strptime(text, DATETIME_FORMAT)


def format_datetime(moment: datetime) -> str:
    """Formata um `datetime` no padrão `YYYY-MM-DDTHH:MM` usado pela API."""
    return moment.strftime(DATETIME_FORMAT)


def _require_non_blank(text: str) -> str:
    if not text.strip():
        raise ValueError("o texto não pode ser vazio nem conter só espaços")
    return text


def _require_email_with_at_sign(text: str) -> str:
    if "@" not in text:
        raise ValueError("o e-mail deve conter '@'")
    return text


def _require_valid_date_text(text: str) -> str:
    parse_date_text(text)
    return text


def _require_date_not_in_future(text: str) -> str:
    if parse_date_text(text) > date.today():
        raise ValueError("a data não pode ser futura")
    return text


def _require_valid_datetime_text(text: str) -> str:
    parse_datetime_text(text)
    return text


NonBlankText = Annotated[str, AfterValidator(_require_non_blank)]
EmailText = Annotated[NonBlankText, AfterValidator(_require_email_with_at_sign)]

# O padrão regex garante o formato rígido (strptime aceitaria "2020-5-1").
DateText = Annotated[
    str,
    StringConstraints(pattern=DATE_PATTERN),
    AfterValidator(_require_valid_date_text),
]
PastOrPresentDateText = Annotated[
    DateText, AfterValidator(_require_date_not_in_future)
]
DateTimeText = Annotated[
    str,
    StringConstraints(pattern=DATETIME_PATTERN),
    AfterValidator(_require_valid_datetime_text),
]

# `strict=True` impede que 10.0 ou "10" sejam aceitos como inteiros (valores em centavos).
NonNegativeInteger = Annotated[int, Field(strict=True, ge=0)]
PositiveInteger = Annotated[int, Field(strict=True, gt=0)]
StrictInteger = Annotated[int, Field(strict=True)]
