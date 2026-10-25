from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

from comum import Inteiro, erro, ou_404
from db import db, inserir, todos, um
import pets
import veterinarios

router = APIRouter(prefix="/agendamentos", tags=["agendamentos"])

FORMATO = "%Y-%m-%dT%H:%M"
# weekday() -> (abre, fecha) em minutos desde 00:00; domingo (6) fechado.
EXPEDIENTE = {**{d: (8 * 60, 18 * 60) for d in range(5)}, 5: (8 * 60, 12 * 60)}


class AgendamentoIn(BaseModel):
    pet_id: Inteiro
    veterinario_id: Inteiro
    inicio: str
    duracao_minutos: Inteiro = 30


class CancelarIn(BaseModel):
    momento: str | None = None


def parse_data_hora(s: str, campo: str) -> datetime:
    try:
        return datetime.strptime(s, FORMATO)
    except ValueError:
        erro(422, f"{campo} deve estar no formato YYYY-MM-DDTHH:MM")


def dentro_do_expediente(inicio: datetime, fim: datetime) -> bool:
    janela = EXPEDIENTE.get(inicio.weekday())
    if janela is None or fim.date() != inicio.date():
        return False
    return janela[0] <= inicio.hour * 60 + inicio.minute and fim.hour * 60 + fim.minute <= janela[1]


def buscar(c, id):
    return ou_404(um(c, "SELECT * FROM agendamentos WHERE id=?", id), "agendamento")


@router.post("", status_code=201)
def criar(body: AgendamentoIn):
    with db() as c:
        # Ordem da SPEC: 404, duração, futuro, expediente, conflito.
        pets.buscar(c, body.pet_id)
        veterinarios.buscar(c, body.veterinario_id)
        if body.duracao_minutos % 15 or not 15 <= body.duracao_minutos <= 120:
            erro(422, "duracao_minutos deve ser múltiplo de 15 entre 15 e 120")
        inicio = parse_data_hora(body.inicio, "inicio")
        if inicio <= datetime.now():
            erro(422, "inicio deve ser futuro")
        fim = inicio + timedelta(minutes=body.duracao_minutos)
        if not dentro_do_expediente(inicio, fim):
            erro(422, "fora do horário de funcionamento")
        i, f = inicio.strftime(FORMATO), fim.strftime(FORMATO)
        if um(c, "SELECT 1 FROM agendamentos WHERE veterinario_id=? AND status IN ('agendado','concluido')"
                 " AND inicio < ? AND fim > ?", body.veterinario_id, f, i):
            erro(409, "veterinário já possui agendamento neste horário")
        id = inserir(c, "INSERT INTO agendamentos(pet_id,veterinario_id,inicio,fim,duracao_minutos,status)"
                        " VALUES(?,?,?,?,?,'agendado')", body.pet_id, body.veterinario_id, i, f, body.duracao_minutos)
        return buscar(c, id)


@router.get("")
def listar(veterinario_id: int | None = None, data: str | None = None):
    sql, args = "SELECT * FROM agendamentos WHERE 1=1", []
    if veterinario_id is not None:
        sql += " AND veterinario_id=?"
        args.append(veterinario_id)
    if data is not None:
        sql += " AND substr(inicio,1,10)=?"
        args.append(data)
    with db() as c:
        return todos(c, sql + " ORDER BY inicio, id", *args)


@router.get("/{id}")
def obter(id: int):
    with db() as c:
        return buscar(c, id)


@router.post("/{id}/cancelar")
def cancelar(id: int, body: CancelarIn | None = None):
    with db() as c:
        ag = buscar(c, id)
        momento = datetime.now()
        if body and body.momento is not None:
            momento = parse_data_hora(body.momento, "momento")
        if ag["status"] != "agendado":
            erro(409, "só agendamentos com status agendado podem ser cancelados")
        antecedencia = datetime.strptime(ag["inicio"], FORMATO) - momento
        status = "cancelado" if antecedencia >= timedelta(hours=24) else "cancelado_tardio"
        c.execute("UPDATE agendamentos SET status=? WHERE id=?", (status, id))
        return buscar(c, id)
