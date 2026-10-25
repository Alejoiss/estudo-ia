"""Testes ocultos da tarefa T3 (plano de fidelidade). Não são vistos pelo agente."""
from aceite_util import SEG, ok


def _fatura(api, agendar, novo_pet, tutor_id, produtos=()):
    a = ok(agendar(f"{SEG}T09:00", pet_id=novo_pet(tutor_id=tutor_id)["id"]), 201)
    body = {"anotacoes": "", "produtos": [{"produto_id": p, "quantidade": q} for p, q in produtos]}
    at = ok(api.post(f"/agendamentos/{a['id']}/atendimento", json=body), 201)
    return ok(api.get(f"/faturas/{at['fatura_id']}"), 200)


def _plano(api, tid, plano):
    return ok(api.put(f"/tutores/{tid}/plano", json={"plano": plano}), 200)


def test_t3_plano_padrao_e_alteracao(api, novo_tutor):
    tid = novo_tutor()["id"]
    assert ok(api.get(f"/tutores/{tid}/plano"), 200) == {"tutor_id": tid, "plano": "nenhum"}
    assert _plano(api, tid, "ouro") == {"tutor_id": tid, "plano": "ouro"}
    assert ok(api.get(f"/tutores/{tid}/plano"), 200)["plano"] == "ouro"
    assert set(ok(api.get(f"/tutores/{tid}"), 200)) == {"id", "nome", "email", "telefone"}


def test_t3_plano_validacoes(api, novo_tutor):
    tid = novo_tutor()["id"]
    ok(api.put(f"/tutores/{tid}/plano", json={"plano": "diamante"}), 422)
    ok(api.put(f"/tutores/{tid}/plano", json={}), 422)
    ok(api.get("/tutores/999999/plano"), 404)
    ok(api.put("/tutores/999999/plano", json={"plano": "ouro"}), 404)


def test_t3_sem_plano_sem_desconto(api, agendar, novo_pet, novo_tutor):
    f = _fatura(api, agendar, novo_pet, novo_tutor()["id"])
    assert f["desconto_centavos"] == 0 and f["total_centavos"] == 15000


def test_t3_desconto_ouro_so_na_consulta(api, agendar, novo_pet, novo_tutor, novo_produto):
    tid = novo_tutor()["id"]
    _plano(api, tid, "ouro")
    pr = novo_produto(preco_centavos=2500, estoque=5)
    f = _fatura(api, agendar, novo_pet, tid, [(pr["id"], 2)])
    assert f["desconto_centavos"] == 3000
    assert [i["total_centavos"] for i in f["itens"]] == [15000, 5000]
    assert f["total_centavos"] == 17000


def test_t3_desconto_prata(api, agendar, novo_pet, novo_tutor):
    tid = novo_tutor()["id"]
    _plano(api, tid, "prata")
    f = _fatura(api, agendar, novo_pet, tid)
    assert f["desconto_centavos"] == 1500 and f["total_centavos"] == 13500


def test_t3_mudar_plano_nao_altera_fatura_existente(api, agendar, novo_pet, novo_tutor):
    tid = novo_tutor()["id"]
    _plano(api, tid, "ouro")
    f = _fatura(api, agendar, novo_pet, tid)
    _plano(api, tid, "nenhum")
    depois = ok(api.get(f"/faturas/{f['id']}"), 200)
    assert depois["desconto_centavos"] == 3000 and depois["total_centavos"] == 12000
    nova = _fatura(api, agendar, novo_pet, tid)
    assert nova["desconto_centavos"] == 0


def test_t3_item_adicionado_e_pagamento_mantem_desconto(api, agendar, novo_pet, novo_tutor):
    tid = novo_tutor()["id"]
    _plano(api, tid, "prata")
    f = _fatura(api, agendar, novo_pet, tid)
    f2 = ok(api.post(f"/faturas/{f['id']}/itens",
                     json={"descricao": "Banho", "quantidade": 1, "valor_unitario_centavos": 4000}), 200)
    assert f2["desconto_centavos"] == 1500 and f2["total_centavos"] == 17500
    pago = ok(api.post(f"/faturas/{f['id']}/pagar"), 200)
    assert pago["desconto_centavos"] == 1500 and pago["total_centavos"] == 17500
    listadas = ok(api.get(f"/tutores/{tid}/faturas"), 200)
    assert listadas[0]["desconto_centavos"] == 1500
