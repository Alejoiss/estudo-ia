from fastapi import APIRouter, Response
from pydantic import BaseModel, field_validator

from comum import Texto, erro, ou_404
from db import db, inserir, todos, um
import faturas

router = APIRouter(prefix="/tutores", tags=["tutores"])


class TutorIn(BaseModel):
    nome: Texto
    email: Texto
    telefone: str | None = None

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        if "@" not in v:
            raise ValueError("email deve conter @")
        return v


def buscar(c, id):
    return ou_404(um(c, "SELECT * FROM tutores WHERE id=?", id), "tutor")


@router.post("", status_code=201)
def criar(body: TutorIn):
    with db() as c:
        id = inserir(c, "INSERT INTO tutores(nome,email,telefone) VALUES(?,?,?)", body.nome, body.email, body.telefone)
        return buscar(c, id)


@router.get("")
def listar():
    with db() as c:
        return todos(c, "SELECT * FROM tutores ORDER BY id")


@router.get("/{id}")
def obter(id: int):
    with db() as c:
        return buscar(c, id)


@router.put("/{id}")
def atualizar(id: int, body: TutorIn):
    with db() as c:
        buscar(c, id)
        c.execute("UPDATE tutores SET nome=?,email=?,telefone=? WHERE id=?", (body.nome, body.email, body.telefone, id))
        return buscar(c, id)


@router.delete("/{id}", status_code=204)
def remover(id: int):
    with db() as c:
        buscar(c, id)
        if um(c, "SELECT 1 FROM pets WHERE tutor_id=?", id):
            erro(409, "tutor possui pets")
        c.execute("DELETE FROM tutores WHERE id=?", (id,))
    return Response(status_code=204)


@router.get("/{id}/pets")
def pets(id: int):
    with db() as c:
        buscar(c, id)
        return todos(c, "SELECT * FROM pets WHERE tutor_id=? ORDER BY id", id)


@router.get("/{id}/faturas")
def faturas_do_tutor(id: int):
    with db() as c:
        buscar(c, id)
        ids = [r["id"] for r in todos(c, "SELECT id FROM faturas WHERE tutor_id=? ORDER BY id", id)]
        return [faturas.montar(c, i) for i in ids]
