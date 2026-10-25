"""Atendimentos (baixa de estoque, atomicidade) e faturas."""
from aceite_util import SEG, TER, ok


def test_atendimento_completo(api, novo_tutor, novo_pet, agendar, novo_produto):
    t = novo_tutor()
    p = novo_pet(tutor_id=t["id"])
    a = ok(agendar(f"{SEG}T09:00", pet_id=p["id"]), 201)
    vacina = novo_produto(nome="Vacina V10", preco_centavos=8000, estoque=5)
    vermi = novo_produto(nome="Vermífugo", preco_centavos=2500, estoque=4)
    body = {"anotacoes": "Animal saudável.", "produtos": [
        {"produto_id": vacina["id"], "quantidade": 1},
        {"produto_id": vermi["id"], "quantidade": 2},
    ]}
    at = ok(api.post(f"/agendamentos/{a['id']}/atendimento", json=body), 201)
    assert at["agendamento_id"] == a["id"] and at["anotacoes"] == "Animal saudável."
    assert at["produtos"] == body["produtos"]
    assert ok(api.get(f"/atendimentos/{at['id']}"), 200) == at

    assert ok(api.get(f"/agendamentos/{a['id']}"), 200)["status"] == "concluido"
    assert ok(api.get(f"/produtos/{vacina['id']}"), 200)["estoque"] == 4
    assert ok(api.get(f"/produtos/{vermi['id']}"), 200)["estoque"] == 2

    f = ok(api.get(f"/faturas/{at['fatura_id']}"), 200)
    assert f["tutor_id"] == t["id"] and f["atendimento_id"] == at["id"] and f["status"] == "aberta"
    assert f["itens"] == [
        {"descricao": "Consulta", "quantidade": 1, "valor_unitario_centavos": 15000, "total_centavos": 15000},
        {"descricao": "Vacina V10", "quantidade": 1, "valor_unitario_centavos": 8000, "total_centavos": 8000},
        {"descricao": "Vermífugo", "quantidade": 2, "valor_unitario_centavos": 2500, "total_centavos": 5000},
    ]
    assert f["total_centavos"] == 28000
    assert [x["id"] for x in ok(api.get(f"/tutores/{t['id']}/faturas"), 200)] == [f["id"]]


def test_atendimento_sem_produtos(api, agendar):
    a = ok(agendar(f"{SEG}T09:00"), 201)
    at = ok(api.post(f"/agendamentos/{a['id']}/atendimento", json={"anotacoes": "", "produtos": []}), 201)
    f = ok(api.get(f"/faturas/{at['fatura_id']}"), 200)
    assert len(f["itens"]) == 1 and f["total_centavos"] == 15000


def test_estoque_insuficiente_nao_altera_nada(api, novo_tutor, novo_pet, agendar, novo_produto):
    t = novo_tutor()
    a = ok(agendar(f"{SEG}T09:00", pet_id=novo_pet(tutor_id=t["id"])["id"]), 201)
    farto = novo_produto(estoque=10)
    escasso = novo_produto(estoque=1)
    body = {"anotacoes": "x", "produtos": [
        {"produto_id": farto["id"], "quantidade": 3},
        {"produto_id": escasso["id"], "quantidade": 2},
    ]}
    ok(api.post(f"/agendamentos/{a['id']}/atendimento", json=body), 409)
    assert ok(api.get(f"/produtos/{farto['id']}"), 200)["estoque"] == 10
    assert ok(api.get(f"/produtos/{escasso['id']}"), 200)["estoque"] == 1
    assert ok(api.get(f"/agendamentos/{a['id']}"), 200)["status"] == "agendado"
    assert ok(api.get(f"/tutores/{t['id']}/faturas"), 200) == []


def test_atendimento_regras_de_estado_e_404(api, agendar, novo_produto):
    a = ok(agendar(f"{TER}T09:00"), 201)
    ok(api.post(f"/agendamentos/{a['id']}/cancelar", json={"momento": f"{SEG}T08:00"}), 200)
    ok(api.post(f"/agendamentos/{a['id']}/atendimento", json={"anotacoes": "", "produtos": []}), 409)
    ok(api.post("/agendamentos/999999/atendimento", json={"anotacoes": "", "produtos": []}), 404)
    b = ok(agendar(f"{TER}T10:00"), 201)
    ok(api.post(f"/agendamentos/{b['id']}/atendimento",
                json={"anotacoes": "", "produtos": [{"produto_id": 999999, "quantidade": 1}]}), 404)
    ok(api.post(f"/agendamentos/{b['id']}/atendimento",
                json={"anotacoes": "", "produtos": [{"produto_id": novo_produto()["id"], "quantidade": 0}]}), 422)
    ok(api.post(f"/agendamentos/{b['id']}/atendimento", json={"anotacoes": "", "produtos": []}), 201)
    ok(api.post(f"/agendamentos/{b['id']}/atendimento", json={"anotacoes": "", "produtos": []}), 409)
    ok(api.get("/atendimentos/999999"), 404)


def test_agendamento_concluido_continua_ocupando_horario(api, agendar, novo_vet):
    vid = novo_vet()["id"]
    a = ok(agendar(f"{SEG}T16:00", vet_id=vid), 201)
    ok(api.post(f"/agendamentos/{a['id']}/atendimento", json={"anotacoes": "", "produtos": []}), 201)
    ok(agendar(f"{SEG}T16:00", vet_id=vid), 409)


def _fatura_aberta(api, agendar):
    a = ok(agendar(f"{SEG}T09:00"), 201)
    at = ok(api.post(f"/agendamentos/{a['id']}/atendimento", json={"anotacoes": "", "produtos": []}), 201)
    return at["fatura_id"]


def test_adicionar_item_e_pagar(api, agendar):
    fid = _fatura_aberta(api, agendar)
    f = ok(api.post(f"/faturas/{fid}/itens",
                    json={"descricao": "Banho", "quantidade": 2, "valor_unitario_centavos": 3000}), 200)
    assert f["itens"][-1] == {"descricao": "Banho", "quantidade": 2, "valor_unitario_centavos": 3000, "total_centavos": 6000}
    assert f["total_centavos"] == 21000
    pago = ok(api.post(f"/faturas/{fid}/pagar"), 200)
    assert pago["status"] == "paga" and pago["total_centavos"] == 21000


def test_fatura_paga_nao_pode_ser_alterada(api, agendar):
    fid = _fatura_aberta(api, agendar)
    ok(api.post(f"/faturas/{fid}/pagar"), 200)
    ok(api.post(f"/faturas/{fid}/pagar"), 409)
    ok(api.post(f"/faturas/{fid}/itens",
                json={"descricao": "Extra", "quantidade": 1, "valor_unitario_centavos": 100}), 409)
    assert ok(api.get(f"/faturas/{fid}"), 200)["total_centavos"] == 15000


def test_fatura_validacoes_e_404(api, agendar):
    fid = _fatura_aberta(api, agendar)
    ok(api.post(f"/faturas/{fid}/itens", json={"descricao": "X", "quantidade": 0, "valor_unitario_centavos": 100}), 422)
    ok(api.post(f"/faturas/{fid}/itens", json={"descricao": "X", "quantidade": 1, "valor_unitario_centavos": 1.5}), 422)
    ok(api.get("/faturas/999999"), 404)
    ok(api.post("/faturas/999999/pagar"), 404)
