from fastapi import APIRouter
from pydantic import BaseModel

from comum import InteiroNaoNeg, InteiroPositivo, Texto, erro, ou_404
from db import db, inserir, todos, um

router = APIRouter(prefix="/faturas", tags=["faturas"])


class ItemIn(BaseModel):
    descricao: Texto
    quantidade: InteiroPositivo
    valor_unitario_centavos: InteiroNaoNeg


def adicionar_item(c, fatura_id, descricao, quantidade, valor_unitario_centavos):
    inserir(c, "INSERT INTO fatura_itens(fatura_id,descricao,quantidade,valor_unitario_centavos) VALUES(?,?,?,?)",
            fatura_id, descricao, quantidade, valor_unitario_centavos)


def montar(c, id):
    """Fatura com itens e total calculados."""
    f = ou_404(um(c, "SELECT * FROM faturas WHERE id=?", id), "fatura")
    itens = todos(c, "SELECT descricao,quantidade,valor_unitario_centavos FROM fatura_itens WHERE fatura_id=? ORDER BY id", id)
    for i in itens:
        i["total_centavos"] = i["quantidade"] * i["valor_unitario_centavos"]
    f["itens"] = itens
    f["total_centavos"] = sum(i["total_centavos"] for i in itens)
    return f


def _aberta(c, id):
    f = montar(c, id)
    if f["status"] == "paga":
        erro(409, "fatura já paga")
    return f


@router.get("/{id}")
def obter(id: int):
    with db() as c:
        return montar(c, id)


@router.post("/{id}/itens")
def novo_item(id: int, body: ItemIn):
    with db() as c:
        _aberta(c, id)
        adicionar_item(c, id, body.descricao, body.quantidade, body.valor_unitario_centavos)
        return montar(c, id)


@router.post("/{id}/pagar")
def pagar(id: int):
    with db() as c:
        _aberta(c, id)
        c.execute("UPDATE faturas SET status='paga' WHERE id=?", (id,))
        return montar(c, id)
