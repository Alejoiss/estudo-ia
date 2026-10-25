"""Testes ocultos da tarefa T5 (nova política de cancelamento). Não são vistos pelo agente."""
from aceite_util import SEG, TER, ok

TAXA = {"descricao": "Taxa de cancelamento tardio", "quantidade": 1,
        "valor_unitario_centavos": 5000, "total_centavos": 5000}


def _ag(agendar, novo_pet, tid, inicio):
    return ok(agendar(inicio, pet_id=novo_pet(tutor_id=tid)["id"]), 201)


def _cancelar(api, aid, momento):
    return ok(api.post(f"/agendamentos/{aid}/cancelar", json={"momento": momento}), 200)


def test_t5_doze_horas_ou_mais_sem_custo(api, agendar, novo_pet, novo_tutor):
    tid = novo_tutor()["id"]
    a = _ag(agendar, novo_pet, tid, f"{TER}T10:00")
    assert _cancelar(api, a["id"], f"{SEG}T22:00")["status"] == "cancelado"   # exatamente 12 h
    b = _ag(agendar, novo_pet, tid, f"{TER}T11:00")
    assert _cancelar(api, b["id"], f"{SEG}T12:00")["status"] == "cancelado"   # 23 h (era tardio antes)
    assert ok(api.get(f"/tutores/{tid}/faturas"), 200) == []


def test_t5_menos_de_doze_horas_gera_taxa(api, agendar, novo_pet, novo_tutor):
    tid = novo_tutor()["id"]
    a = _ag(agendar, novo_pet, tid, f"{TER}T10:00")
    assert _cancelar(api, a["id"], f"{SEG}T22:01")["status"] == "cancelado_tardio"
    faturas = ok(api.get(f"/tutores/{tid}/faturas"), 200)
    assert len(faturas) == 1
    f = faturas[0]
    assert f["tutor_id"] == tid and f["atendimento_id"] is None and f["status"] == "aberta"
    assert f["itens"] == [TAXA] and f["total_centavos"] == 5000
    assert ok(api.get(f"/faturas/{f['id']}"), 200)["itens"] == [TAXA]


def test_t5_taxa_pode_ser_paga(api, agendar, novo_pet, novo_tutor):
    tid = novo_tutor()["id"]
    a = _ag(agendar, novo_pet, tid, f"{TER}T10:00")
    _cancelar(api, a["id"], f"{TER}T09:00")
    fid = ok(api.get(f"/tutores/{tid}/faturas"), 200)[0]["id"]
    assert ok(api.post(f"/faturas/{fid}/pagar"), 200)["status"] == "paga"


def test_t5_cancelar_de_novo_nao_gera_segunda_taxa(api, agendar, novo_pet, novo_tutor):
    tid = novo_tutor()["id"]
    a = _ag(agendar, novo_pet, tid, f"{TER}T10:00")
    _cancelar(api, a["id"], f"{TER}T08:00")
    ok(api.post(f"/agendamentos/{a['id']}/cancelar", json={"momento": f"{TER}T08:30"}), 409)
    assert len(ok(api.get(f"/tutores/{tid}/faturas"), 200)) == 1


def test_t5_taxa_vai_para_o_tutor_certo(api, agendar, novo_pet, novo_tutor):
    t1, t2 = novo_tutor()["id"], novo_tutor()["id"]
    a = _ag(agendar, novo_pet, t2, f"{TER}T10:00")
    _cancelar(api, a["id"], f"{TER}T07:00")
    assert ok(api.get(f"/tutores/{t1}/faturas"), 200) == []
    assert len(ok(api.get(f"/tutores/{t2}/faturas"), 200)) == 1
