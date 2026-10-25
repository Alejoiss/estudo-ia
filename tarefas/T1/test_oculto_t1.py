"""Testes ocultos da tarefa T1 (vacinas). Não são vistos pelo agente."""
from datetime import date, timedelta

from aceite_util import ok


def _vac(api, pet_id, vet_id, **extra):
    body = {"pet_id": pet_id, "veterinario_id": vet_id, "nome_vacina": "V10",
            "data_aplicacao": "2025-01-10", "intervalo_reforco_dias": 365}
    body.update(extra)
    return api.post("/vacinas", json=body)


def test_t1_criar_e_obter(api, novo_pet, novo_vet):
    p, v = novo_pet(), novo_vet()
    vac = ok(_vac(api, p["id"], v["id"], data_aplicacao="2025-01-10", intervalo_reforco_dias=30), 201)
    assert vac["data_reforco"] == "2025-02-09"
    for k, val in {"pet_id": p["id"], "veterinario_id": v["id"], "nome_vacina": "V10",
                   "data_aplicacao": "2025-01-10", "intervalo_reforco_dias": 30}.items():
        assert vac[k] == val
    assert isinstance(vac["id"], int)
    assert ok(api.get(f"/vacinas/{vac['id']}"), 200) == vac


def test_t1_data_reforco_ignora_valor_do_cliente(api, novo_pet, novo_vet):
    vac = ok(_vac(api, novo_pet()["id"], novo_vet()["id"], intervalo_reforco_dias=1,
                  data_aplicacao="2024-02-28", data_reforco="2000-01-01"), 201)
    assert vac["data_reforco"] == "2024-02-29"


def test_t1_atualizar_recalcula(api, novo_pet, novo_vet):
    p, v = novo_pet(), novo_vet()
    vac = ok(_vac(api, p["id"], v["id"]), 201)
    body = {"pet_id": p["id"], "veterinario_id": v["id"], "nome_vacina": "Antirrábica",
            "data_aplicacao": "2025-03-01", "intervalo_reforco_dias": 10}
    upd = ok(api.put(f"/vacinas/{vac['id']}", json=body), 200)
    assert upd["id"] == vac["id"] and upd["nome_vacina"] == "Antirrábica" and upd["data_reforco"] == "2025-03-11"
    assert ok(api.get(f"/vacinas/{vac['id']}"), 200) == upd


def test_t1_excluir(api, novo_pet, novo_vet):
    vac = ok(_vac(api, novo_pet()["id"], novo_vet()["id"]), 201)
    ok(api.delete(f"/vacinas/{vac['id']}"), 204)
    ok(api.get(f"/vacinas/{vac['id']}"), 404)


def test_t1_inexistentes(api, novo_pet, novo_vet):
    p, v = novo_pet(), novo_vet()
    ok(_vac(api, p["id"], v["id"]), 201)  # garante que a rota existe (rota ausente também dá 404)
    ok(_vac(api, 999999, v["id"]), 404)
    ok(_vac(api, p["id"], 999999), 404)
    ok(api.get("/vacinas/999999"), 404)
    ok(api.delete("/vacinas/999999"), 404)
    body = {"pet_id": p["id"], "veterinario_id": v["id"], "nome_vacina": "X",
            "data_aplicacao": "2025-01-01", "intervalo_reforco_dias": 1}
    ok(api.put("/vacinas/999999", json=body), 404)
    ok(api.get("/pets/999999/vacinas"), 404)


def test_t1_validacoes(api, novo_pet, novo_vet):
    p, v = novo_pet()["id"], novo_vet()["id"]
    futura = (date.today() + timedelta(days=5)).isoformat()
    ok(_vac(api, p, v, data_aplicacao=futura), 422)
    ok(_vac(api, p, v, intervalo_reforco_dias=0), 422)
    ok(_vac(api, p, v, intervalo_reforco_dias=-3), 422)
    ok(_vac(api, p, v, nome_vacina="  "), 422)
    ok(_vac(api, p, v, data_aplicacao="10/01/2025"), 422)


def test_t1_listagem_por_pet_ordenada(api, novo_pet, novo_vet):
    p, outro, v = novo_pet(), novo_pet(), novo_vet()
    a = ok(_vac(api, p["id"], v["id"], data_aplicacao="2024-05-01"), 201)
    b = ok(_vac(api, p["id"], v["id"], data_aplicacao="2025-02-01"), 201)
    c = ok(_vac(api, p["id"], v["id"], data_aplicacao="2024-05-01"), 201)
    ok(_vac(api, outro["id"], v["id"]), 201)
    lst = ok(api.get(f"/pets/{p['id']}/vacinas"), 200)
    assert [x["id"] for x in lst] == [b["id"], a["id"], c["id"]]
    assert ok(api.get(f"/pets/{novo_pet()['id']}/vacinas"), 200) == []


def test_t1_reforcos_pendentes(api, novo_pet, novo_vet):
    p, v = novo_pet()["id"], novo_vet()["id"]
    r1 = ok(_vac(api, p, v, data_aplicacao="2023-01-01", intervalo_reforco_dias=100), 201)  # 2023-04-11
    r2 = ok(_vac(api, p, v, data_aplicacao="2023-01-01", intervalo_reforco_dias=40), 201)   # 2023-02-10
    r3 = ok(_vac(api, p, v, data_aplicacao="2023-01-01", intervalo_reforco_dias=101), 201)  # 2023-04-12
    lst = ok(api.get("/vacinas/reforcos-pendentes", params={"ate": "2023-04-11"}), 200)
    ids = [x["id"] for x in lst]
    assert r2["id"] in ids and r1["id"] in ids and r3["id"] not in ids
    assert ids.index(r2["id"]) < ids.index(r1["id"])
    assert all(x["data_reforco"] <= "2023-04-11" for x in lst)
    datas = [x["data_reforco"] for x in lst]
    assert datas == sorted(datas)


def test_t1_reforcos_pendentes_validacao(api):
    ok(api.get("/vacinas/reforcos-pendentes"), 422)
    ok(api.get("/vacinas/reforcos-pendentes", params={"ate": "amanha"}), 422)


def test_t1_pet_com_vacina_nao_pode_ser_excluido(api, novo_pet, novo_vet):
    p = novo_pet()
    vac = ok(_vac(api, p["id"], novo_vet()["id"]), 201)
    ok(api.delete(f"/pets/{p['id']}"), 409)
    ok(api.delete(f"/vacinas/{vac['id']}"), 204)
    ok(api.delete(f"/pets/{p['id']}"), 204)
