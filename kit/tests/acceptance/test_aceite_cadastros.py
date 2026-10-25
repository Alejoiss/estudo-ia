"""Tutores, pets, veterinários e produtos."""
from aceite_util import ok


# ---------- Tutores ----------

def test_tutor_crud(api, novo_tutor):
    t = novo_tutor(nome="João", telefone=None)
    assert t["nome"] == "João" and t["telefone"] is None and isinstance(t["id"], int)
    assert ok(api.get(f"/tutores/{t['id']}"), 200) == t
    body = {"nome": "João Silva", "email": "joao@ex.com", "telefone": "4633330000"}
    upd = ok(api.put(f"/tutores/{t['id']}", json=body), 200)
    assert upd == {"id": t["id"], **body}
    assert any(x["id"] == t["id"] for x in ok(api.get("/tutores"), 200))
    ok(api.delete(f"/tutores/{t['id']}"), 204)
    ok(api.get(f"/tutores/{t['id']}"), 404)


def test_tutor_listagem_ordenada_por_id(api, novo_tutor):
    novo_tutor(); novo_tutor()
    ids = [x["id"] for x in ok(api.get("/tutores"), 200)]
    assert ids == sorted(ids)


def test_tutor_validacoes(api):
    ok(api.post("/tutores", json={"nome": "   ", "email": "a@b.com"}), 422)
    ok(api.post("/tutores", json={"nome": "Ana", "email": "sem-arroba"}), 422)
    ok(api.post("/tutores", json={"email": "a@b.com"}), 422)


def test_tutor_inexistente(api):
    ok(api.get("/tutores/999999"), 404)
    ok(api.put("/tutores/999999", json={"nome": "X", "email": "x@x.com"}), 404)
    ok(api.delete("/tutores/999999"), 404)
    ok(api.get("/tutores/999999/pets"), 404)
    ok(api.get("/tutores/999999/faturas"), 404)


def test_tutor_com_pets_nao_pode_ser_excluido(api, novo_tutor, novo_pet):
    t = novo_tutor()
    p = novo_pet(tutor_id=t["id"])
    ok(api.delete(f"/tutores/{t['id']}"), 409)
    ok(api.delete(f"/pets/{p['id']}"), 204)
    ok(api.delete(f"/tutores/{t['id']}"), 204)


# ---------- Pets ----------

def test_pet_crud(api, novo_tutor, novo_pet):
    t = novo_tutor()
    p = novo_pet(tutor_id=t["id"], nome="Mia", especie="gato", data_nascimento=None)
    assert p["tutor_id"] == t["id"] and p["especie"] == "gato" and p["data_nascimento"] is None
    assert ok(api.get(f"/pets/{p['id']}"), 200) == p
    body = {"nome": "Mia", "especie": "gato", "tutor_id": t["id"], "data_nascimento": "2021-01-10"}
    assert ok(api.put(f"/pets/{p['id']}", json=body), 200)["data_nascimento"] == "2021-01-10"
    assert [x["id"] for x in ok(api.get(f"/tutores/{t['id']}/pets"), 200)] == [p["id"]]
    ok(api.delete(f"/pets/{p['id']}"), 204)
    ok(api.get(f"/pets/{p['id']}"), 404)


def test_pet_validacoes(api, novo_tutor):
    tid = novo_tutor()["id"]
    ok(api.post("/pets", json={"nome": "X", "especie": "dragao", "tutor_id": tid}), 422)
    ok(api.post("/pets", json={"nome": "", "especie": "cao", "tutor_id": tid}), 422)
    ok(api.post("/pets", json={"nome": "X", "especie": "cao", "tutor_id": tid, "data_nascimento": "2099-01-01"}), 422)
    ok(api.post("/pets", json={"nome": "X", "especie": "cao", "tutor_id": tid, "data_nascimento": "01/02/2020"}), 422)


def test_pet_tutor_inexistente(api):
    ok(api.post("/pets", json={"nome": "X", "especie": "cao", "tutor_id": 999999}), 404)
    ok(api.get("/pets/999999"), 404)


def test_pet_com_agendamento_nao_pode_ser_excluido(api, novo_pet, agendar):
    p = novo_pet()
    ok(agendar(f"2030-03-04T09:00", pet_id=p["id"]), 201)
    ok(api.delete(f"/pets/{p['id']}"), 409)


# ---------- Veterinários ----------

def test_veterinario_crud_e_crmv_unico(api, novo_vet):
    v = novo_vet()
    assert ok(api.get(f"/veterinarios/{v['id']}"), 200) == v
    assert any(x["id"] == v["id"] for x in ok(api.get("/veterinarios"), 200))
    ok(api.post("/veterinarios", json={"nome": "Outro", "crmv": v["crmv"]}), 409)
    ok(api.post("/veterinarios", json={"nome": "Sem crmv"}), 422)
    ok(api.get("/veterinarios/999999"), 404)


# ---------- Produtos ----------

def test_produto_crud_e_entrada(api, novo_produto):
    pr = novo_produto(estoque=3)
    assert ok(api.get(f"/produtos/{pr['id']}"), 200) == pr
    assert any(x["id"] == pr["id"] for x in ok(api.get("/produtos"), 200))
    assert ok(api.post(f"/produtos/{pr['id']}/entrada", json={"quantidade": 4}), 200)["estoque"] == 7
    ok(api.post(f"/produtos/{pr['id']}/entrada", json={"quantidade": 0}), 422)
    ok(api.post("/produtos/999999/entrada", json={"quantidade": 1}), 404)
    ok(api.get("/produtos/999999"), 404)


def test_produto_validacoes(api):
    base = {"nome": "Ração", "preco_centavos": 1000, "estoque": 1, "estoque_minimo": 0}
    ok(api.post("/produtos", json={**base, "preco_centavos": 10.5}), 422)
    ok(api.post("/produtos", json={**base, "preco_centavos": -1}), 422)
    ok(api.post("/produtos", json={**base, "estoque": -1}), 422)
    ok(api.post("/produtos", json={**base, "nome": " "}), 422)
