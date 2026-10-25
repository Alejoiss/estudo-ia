from typing import Annotated, NoReturn

from fastapi import HTTPException
from pydantic import Field, StringConstraints

# String obrigatória: sem espaços nas pontas, não vazia.
Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
# Inteiros estritos (rejeitam 10.5 e booleanos).
Inteiro = Annotated[int, Field(strict=True)]
InteiroNaoNeg = Annotated[int, Field(strict=True, ge=0)]
InteiroPositivo = Annotated[int, Field(strict=True, gt=0)]


def erro(status: int, msg: str) -> NoReturn:
    raise HTTPException(status_code=status, detail=msg)


def ou_404(linha, nome: str):
    if linha is None:
        erro(404, f"{nome} não encontrado")
    return linha
