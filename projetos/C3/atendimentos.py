import json

from fastapi import APIRouter
from pydantic import BaseModel

from comum import InteiroPositivo, erro, ou_404
from db import db, inserir, um
import agendamentos
import faturas
import pets
import produtos

router = APIRouter(tags=["atendimentos"])

VALOR_CONSULTA_CENTAVOS = 15000


class ProdutoUsado(BaseModel):
    produto_id: int
    quantidade: InteiroPositivo


class AtendimentoIn(BaseModel):
    anotacoes: str
    produtos: list[ProdutoUsado]


def montar(c, id):
    a = ou_404(um(c, "SELECT * FROM atendimentos WHERE id=?", id), "atendimento")
    fatura = um(c, "SELECT id FROM faturas WHERE atendimento_id=?", id)
    return {"id": a["id"], "agendamento_id": a["agendamento_id"], "anotacoes": a["anotacoes"],
            "produtos": json.loads(a["produtos_json"]), "fatura_id": fatura["id"]}


@router.post("/agendamentos/{id}/atendimento", status_code=201)
def registrar(id: int, body: AtendimentoIn):
    with db() as c:
        ag = agendamentos.buscar(c, id)
        prods = {p.produto_id: produtos.buscar(c, p.produto_id) for p in body.produtos}
        if ag["status"] != "agendado":
            erro(409, "agendamento não está com status agendado")
        usado = {}
        for p in body.produtos:
            usado[p.produto_id] = usado.get(p.produto_id, 0) + p.quantidade
        if any(prods[pid]["estoque"] < q for pid, q in usado.items()):
            erro(409, "estoque insuficiente")

        tutor_id = pets.buscar(c, ag["pet_id"])["tutor_id"]
        c.execute("UPDATE agendamentos SET status='concluido' WHERE id=?", (id,))
        for pid, q in usado.items():
            c.execute("UPDATE produtos SET estoque=estoque-? WHERE id=?", (q, pid))
        enviados = [p.model_dump() for p in body.produtos]
        at_id = inserir(c, "INSERT INTO atendimentos(agendamento_id,anotacoes,produtos_json) VALUES(?,?,?)",
                        id, body.anotacoes, json.dumps(enviados))
        fatura_id = inserir(c, "INSERT INTO faturas(tutor_id,atendimento_id,status) VALUES(?,?,'aberta')", tutor_id, at_id)
        faturas.adicionar_item(c, fatura_id, "Consulta", 1, VALOR_CONSULTA_CENTAVOS)
        for p in body.produtos:
            pr = prods[p.produto_id]
            faturas.adicionar_item(c, fatura_id, pr["nome"], p.quantidade, pr["preco_centavos"])
        return montar(c, at_id)


@router.get("/atendimentos/{id}")
def obter(id: int):
    with db() as c:
        return montar(c, id)
