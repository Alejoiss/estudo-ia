from datetime import date
from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel, field_validator

from comum import InteiroPositivo, Texto, erro, ou_404
from db import db, inserir, um
import tutores

router = APIRouter(prefix="/pets", tags=["pets"])


class PetIn(BaseModel):
    nome: Texto
    especie: Literal["cao", "gato", "outro"]
    tutor_id: InteiroPositivo
    data_nascimento: date | None = None

    @field_validator("data_nascimento")
    @classmethod
    def _nao_futura(cls, v):
        if v is not None and v > date.today():
            raise ValueError("data_nascimento não pode ser futura")
        return v


def buscar(c, id):
    return ou_404(um(c, "SELECT * FROM pets WHERE id=?", id), "pet")


def valores(body: PetIn):
    nasc = body.data_nascimento.isoformat() if body.data_nascimento else None
    return body.nome, body.especie, body.tutor_id, nasc


@router.post("", status_code=201)
def criar(body: PetIn):
    with db() as c:
        tutores.buscar(c, body.tutor_id)
        id = inserir(c, "INSERT INTO pets(nome,especie,tutor_id,data_nascimento) VALUES(?,?,?,?)", *valores(body))
        return buscar(c, id)


@router.get("/{id}")
def obter(id: int):
    with db() as c:
        return buscar(c, id)


@router.put("/{id}")
def atualizar(id: int, body: PetIn):
    with db() as c:
        buscar(c, id)
        tutores.buscar(c, body.tutor_id)
        c.execute("UPDATE pets SET nome=?,especie=?,tutor_id=?,data_nascimento=? WHERE id=?", (*valores(body), id))
        return buscar(c, id)


@router.delete("/{id}", status_code=204)
def remover(id: int):
    with db() as c:
        buscar(c, id)
        if um(c, "SELECT 1 FROM agendamentos WHERE pet_id=?", id):
            erro(409, "pet possui agendamentos")
        c.execute("DELETE FROM pets WHERE id=?", (id,))
    return Response(status_code=204)
