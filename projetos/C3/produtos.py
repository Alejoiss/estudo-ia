from fastapi import APIRouter
from pydantic import BaseModel

from comum import InteiroNaoNeg, InteiroPositivo, Texto, ou_404
from db import db, inserir, todos, um

router = APIRouter(prefix="/produtos", tags=["produtos"])


class ProdutoIn(BaseModel):
    nome: Texto
    preco_centavos: InteiroNaoNeg
    estoque: InteiroNaoNeg
    estoque_minimo: InteiroNaoNeg


class EntradaIn(BaseModel):
    quantidade: InteiroPositivo


def buscar(c, id):
    return ou_404(um(c, "SELECT * FROM produtos WHERE id=?", id), "produto")


@router.post("", status_code=201)
def criar(body: ProdutoIn):
    with db() as c:
        id = inserir(c, "INSERT INTO produtos(nome,preco_centavos,estoque,estoque_minimo) VALUES(?,?,?,?)",
                     body.nome, body.preco_centavos, body.estoque, body.estoque_minimo)
        return buscar(c, id)


@router.get("")
def listar():
    with db() as c:
        return todos(c, "SELECT * FROM produtos ORDER BY id")


@router.get("/{id}")
def obter(id: int):
    with db() as c:
        return buscar(c, id)


@router.post("/{id}/entrada")
def entrada(id: int, body: EntradaIn):
    with db() as c:
        buscar(c, id)
        c.execute("UPDATE produtos SET estoque=estoque+? WHERE id=?", (body.quantidade, id))
        return buscar(c, id)
