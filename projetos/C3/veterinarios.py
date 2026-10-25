import sqlite3

from fastapi import APIRouter
from pydantic import BaseModel

from comum import Texto, erro, ou_404
from db import db, inserir, todos, um

router = APIRouter(prefix="/veterinarios", tags=["veterinarios"])


class VeterinarioIn(BaseModel):
    nome: Texto
    crmv: Texto


def buscar(c, id):
    return ou_404(um(c, "SELECT * FROM veterinarios WHERE id=?", id), "veterinário")


@router.post("", status_code=201)
def criar(body: VeterinarioIn):
    with db() as c:
        try:
            id = inserir(c, "INSERT INTO veterinarios(nome,crmv) VALUES(?,?)", body.nome, body.crmv)
        except sqlite3.IntegrityError:
            erro(409, "crmv já cadastrado")
        return buscar(c, id)


@router.get("")
def listar():
    with db() as c:
        return todos(c, "SELECT * FROM veterinarios ORDER BY id")


@router.get("/{id}")
def obter(id: int):
    with db() as c:
        return buscar(c, id)
