import json, os, sqlite3
from datetime import datetime, timedelta
from typing import Annotated, Literal, Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import AfterValidator, BaseModel, StrictInt

db = sqlite3.connect(os.environ.get("DB_PATH", "vetclinic.db"), check_same_thread=False)
db.row_factory = sqlite3.Row
db.executescript("""
create table if not exists tutores(id integer primary key autoincrement, nome, email, telefone);
create table if not exists pets(id integer primary key autoincrement, nome, especie, tutor_id, data_nascimento);
create table if not exists veterinarios(id integer primary key autoincrement, nome, crmv unique);
create table if not exists produtos(id integer primary key autoincrement, nome, preco_centavos, estoque, estoque_minimo);
create table if not exists agendamentos(id integer primary key autoincrement, pet_id, veterinario_id, inicio, fim, duracao_minutos, status);
create table if not exists atendimentos(id integer primary key autoincrement, agendamento_id, anotacoes, produtos, fatura_id);
create table if not exists faturas(id integer primary key autoincrement, tutor_id, atendimento_id, status, itens);
""")
app = FastAPI()
DT = "%Y-%m-%dT%H:%M"
CONSULTA = 15000


def err(code, msg):
    raise HTTPException(code, msg)


def get(table, id):
    row = db.execute(f"select * from {table} where id=?", (id,)).fetchone()
    return dict(row) if row else err(404, f"{table} {id} nao existe")


def insert(table, data):
    cur = db.execute(f"insert into {table}({','.join(data)}) values({','.join('?' * len(data))})", list(data.values()))
    db.commit()
    return get(table, cur.lastrowid)


def update(table, id, data):
    get(table, id)
    db.execute(f"update {table} set {','.join(k + '=?' for k in data)} where id=?", [*data.values(), id])
    db.commit()
    return get(table, id)


def parse(fmt):
    def check(val):
        try:
            datetime.strptime(val, fmt)
        except ValueError:
            raise ValueError("formato invalido")
        return val
    return AfterValidator(check)


def filled(val):
    if not val.strip():
        raise ValueError("vazio")
    return val


def has_at(val):
    if "@" not in filled(val):
        raise ValueError("email invalido")
    return val


def not_future(val):
    if val is not None and datetime.strptime(val, "%Y-%m-%d") > datetime.now():
        raise ValueError("data futura")
    return val


Str = Annotated[str, AfterValidator(filled)]
Day = Annotated[str, parse("%Y-%m-%d")]


def nat(val):
    if val < 0:
        raise ValueError("negativo")
    return val


Nat = Annotated[StrictInt, AfterValidator(nat)]
Qty = Annotated[StrictInt, AfterValidator(lambda val: nat(val - 1) + 1)]


class TutorIn(BaseModel):
    nome: Str
    email: Annotated[str, AfterValidator(has_at)]
    telefone: Optional[str] = None


class PetIn(BaseModel):
    nome: Str
    especie: Literal["cao", "gato", "outro"]
    tutor_id: StrictInt
    data_nascimento: Optional[Annotated[Day, AfterValidator(not_future)]] = None


class VetIn(BaseModel):
    nome: Str
    crmv: Str


class ProdutoIn(BaseModel):
    nome: Str
    preco_centavos: Nat
    estoque: Nat
    estoque_minimo: Nat


class EntradaIn(BaseModel):
    quantidade: Qty


class AgendIn(BaseModel):
    pet_id: StrictInt
    veterinario_id: StrictInt
    inicio: Annotated[str, parse(DT)]
    duracao_minutos: StrictInt = 30


class CancelIn(BaseModel):
    momento: Optional[Annotated[str, parse(DT)]] = None


class UsoIn(BaseModel):
    produto_id: StrictInt
    quantidade: Qty


class AtendIn(BaseModel):
    anotacoes: str
    produtos: list[UsoIn]


class ItemIn(BaseModel):
    descricao: Str
    quantidade: Qty
    valor_unitario_centavos: Nat


@app.post("/tutores", status_code=201)
async def create_tutor(body: TutorIn):
    return insert("tutores", body.model_dump())


@app.get("/tutores")
async def list_tutores():
    return [dict(row) for row in db.execute("select * from tutores order by id")]


@app.get("/tutores/{id}")
async def read_tutor(id: int):
    return get("tutores", id)


@app.put("/tutores/{id}")
async def put_tutor(id: int, body: TutorIn):
    return update("tutores", id, body.model_dump())


@app.delete("/tutores/{id}", status_code=204)
async def delete_tutor(id: int):
    get("tutores", id)
    if db.execute("select 1 from pets where tutor_id=?", (id,)).fetchone():
        err(409, "tutor possui pets")
    db.execute("delete from tutores where id=?", (id,))
    db.commit()
    return Response(status_code=204)


@app.get("/tutores/{id}/pets")
async def tutor_pets(id: int):
    get("tutores", id)
    return [dict(row) for row in db.execute("select * from pets where tutor_id=? order by id", (id,))]


@app.get("/tutores/{id}/faturas")
async def tutor_faturas(id: int):
    get("tutores", id)
    return [fatura(dict(row)) for row in db.execute("select * from faturas where tutor_id=? order by id", (id,))]


@app.post("/pets", status_code=201)
async def create_pet(body: PetIn):
    get("tutores", body.tutor_id)
    return insert("pets", body.model_dump())


@app.get("/pets/{id}")
async def read_pet(id: int):
    return get("pets", id)


@app.put("/pets/{id}")
async def put_pet(id: int, body: PetIn):
    get("pets", id)
    get("tutores", body.tutor_id)
    return update("pets", id, body.model_dump())


@app.delete("/pets/{id}", status_code=204)
async def delete_pet(id: int):
    get("pets", id)
    if db.execute("select 1 from agendamentos where pet_id=?", (id,)).fetchone():
        err(409, "pet possui agendamentos")
    db.execute("delete from pets where id=?", (id,))
    db.commit()
    return Response(status_code=204)


@app.post("/veterinarios", status_code=201)
async def create_vet(body: VetIn):
    if db.execute("select 1 from veterinarios where crmv=?", (body.crmv,)).fetchone():
        err(409, "crmv ja existe")
    return insert("veterinarios", body.model_dump())


@app.get("/veterinarios")
async def list_vets():
    return [dict(row) for row in db.execute("select * from veterinarios order by id")]


@app.get("/veterinarios/{id}")
async def read_vet(id: int):
    return get("veterinarios", id)


@app.post("/produtos", status_code=201)
async def create_produto(body: ProdutoIn):
    return insert("produtos", body.model_dump())


@app.get("/produtos")
async def list_produtos():
    return [dict(row) for row in db.execute("select * from produtos order by id")]


@app.get("/produtos/{id}")
async def read_produto(id: int):
    return get("produtos", id)


@app.post("/produtos/{id}/entrada")
async def entrada_produto(id: int, body: EntradaIn):
    return update("produtos", id, {"estoque": get("produtos", id)["estoque"] + body.quantidade})


def hours(day):
    return {5: (8, 12), 6: None}.get(day.weekday(), (8, 18))


@app.post("/agendamentos", status_code=201)
async def create_agend(body: AgendIn):
    get("pets", body.pet_id)
    get("veterinarios", body.veterinario_id)
    mins = body.duracao_minutos
    if mins % 15 or not 15 <= mins <= 120:
        err(422, "duracao invalida")
    start = datetime.strptime(body.inicio, DT)
    end = start + timedelta(minutes=mins)
    if start <= datetime.now():
        err(422, "inicio deve ser futuro")
    open_close = hours(start)
    if not open_close or start.date() != end.date() or not (
        start.replace(hour=open_close[0], minute=0) <= start and end <= start.replace(hour=open_close[1], minute=0)
    ):
        err(422, "fora do expediente")
    fim = end.strftime(DT)
    if db.execute(
        "select 1 from agendamentos where veterinario_id=? and status in ('agendado','concluido') and inicio<? and fim>?",
        (body.veterinario_id, fim, body.inicio),
    ).fetchone():
        err(409, "conflito de agenda")
    return insert("agendamentos", {
        "pet_id": body.pet_id, "veterinario_id": body.veterinario_id, "inicio": body.inicio,
        "fim": fim, "duracao_minutos": mins, "status": "agendado",
    })


@app.get("/agendamentos/{id}")
async def read_agend(id: int):
    return get("agendamentos", id)


@app.get("/agendamentos")
async def list_agend(veterinario_id: Optional[int] = None, data: Optional[Day] = None):
    rows = db.execute(
        "select * from agendamentos where (?1 is null or veterinario_id=?1) and (?2 is null or substr(inicio,1,10)=?2) order by inicio, id",
        (veterinario_id, data),
    )
    return [dict(row) for row in rows]


@app.post("/agendamentos/{id}/cancelar")
async def cancel_agend(id: int, body: Optional[CancelIn] = None):
    agend = get("agendamentos", id)
    if agend["status"] != "agendado":
        err(409, "agendamento nao esta agendado")
    now = datetime.strptime(body.momento, DT) if body and body.momento else datetime.now()
    late = datetime.strptime(agend["inicio"], DT) - now < timedelta(hours=24)
    return update("agendamentos", id, {"status": "cancelado_tardio" if late else "cancelado"})


def fatura(row):
    row["itens"] = json.loads(row["itens"])
    row["total_centavos"] = sum(item["total_centavos"] for item in row["itens"])
    return row


def item(descricao, quantidade, valor):
    return {"descricao": descricao, "quantidade": quantidade, "valor_unitario_centavos": valor, "total_centavos": quantidade * valor}


@app.post("/agendamentos/{id}/atendimento", status_code=201)
async def create_atend(id: int, body: AtendIn):
    agend = get("agendamentos", id)
    prods = [get("produtos", uso.produto_id) for uso in body.produtos]
    if agend["status"] != "agendado":
        err(409, "agendamento nao esta agendado")
    need = {}
    for uso in body.produtos:
        need[uso.produto_id] = need.get(uso.produto_id, 0) + uso.quantidade
    for pid, qty in need.items():
        if get("produtos", pid)["estoque"] < qty:
            err(409, "estoque insuficiente")
    itens = [item("Consulta", 1, CONSULTA)] + [
        item(prod["nome"], uso.quantidade, prod["preco_centavos"]) for prod, uso in zip(prods, body.produtos)
    ]
    for pid, qty in need.items():
        db.execute("update produtos set estoque=estoque-? where id=?", (qty, pid))
    db.execute("update agendamentos set status='concluido' where id=?", (id,))
    tutor_id = get("pets", agend["pet_id"])["tutor_id"]
    atend = db.execute(
        "insert into atendimentos(agendamento_id, anotacoes, produtos) values(?,?,?)",
        (id, body.anotacoes, json.dumps([uso.model_dump() for uso in body.produtos])),
    ).lastrowid
    fat = db.execute(
        "insert into faturas(tutor_id, atendimento_id, status, itens) values(?,?,'aberta',?)",
        (tutor_id, atend, json.dumps(itens)),
    ).lastrowid
    db.execute("update atendimentos set fatura_id=? where id=?", (fat, atend))
    db.commit()
    return read_atend_row(atend)


def read_atend_row(id):
    row = get("atendimentos", id)
    row["produtos"] = json.loads(row["produtos"])
    return row


@app.get("/atendimentos/{id}")
async def read_atend(id: int):
    return read_atend_row(id)


@app.get("/faturas/{id}")
async def read_fatura(id: int):
    return fatura(get("faturas", id))


@app.post("/faturas/{id}/itens")
async def add_item(id: int, body: ItemIn):
    fat = fatura(get("faturas", id))
    if fat["status"] == "paga":
        err(409, "fatura paga")
    itens = fat["itens"] + [item(body.descricao, body.quantidade, body.valor_unitario_centavos)]
    return fatura(update("faturas", id, {"itens": json.dumps(itens)}))


@app.post("/faturas/{id}/pagar")
async def pay_fatura(id: int):
    if get("faturas", id)["status"] == "paga":
        err(409, "fatura ja paga")
    return fatura(update("faturas", id, {"status": "paga"}))
