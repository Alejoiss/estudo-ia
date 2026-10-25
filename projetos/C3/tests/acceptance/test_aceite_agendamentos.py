"""Agendamentos: criação, expediente, conflitos, listagem e cancelamento."""
from aceite_util import DOM, SAB, SEG, TER, ok


def test_criacao_basica(api, agendar):
    a = ok(agendar(f"{SEG}T09:00"), 201)
    assert a["status"] == "agendado" and a["duracao_minutos"] == 30
    assert a["inicio"] == f"{SEG}T09:00" and a["fim"] == f"{SEG}T09:30"
    assert ok(api.get(f"/agendamentos/{a['id']}"), 200) == a


def test_duracao_personalizada(agendar):
    a = ok(agendar(f"{SEG}T14:00", duracao=60), 201)
    assert a["fim"] == f"{SEG}T15:00"


def test_duracao_invalida(agendar):
    ok(agendar(f"{SEG}T14:00", duracao=20), 422)
    ok(agendar(f"{SEG}T14:00", duracao=0), 422)
    ok(agendar(f"{SEG}T14:00", duracao=135), 422)


def test_pet_ou_vet_inexistente(agendar):
    ok(agendar(f"{SEG}T09:00", pet_id=999999), 404)
    ok(agendar(f"{SEG}T09:00", vet_id=999999), 404)


def test_inicio_no_passado(agendar):
    ok(agendar("2020-01-06T10:00"), 422)


def test_formato_de_data_invalido(agendar):
    ok(agendar("04/03/2030 09:00"), 422)


def test_expediente_dia_util(agendar):
    ok(agendar(f"{TER}T08:00"), 201)
    ok(agendar(f"{TER}T17:30"), 201)
    ok(agendar(f"{TER}T07:45"), 422)
    ok(agendar(f"{TER}T17:45"), 422)
    ok(agendar(f"{TER}T18:00"), 422)


def test_expediente_sabado_e_domingo(agendar):
    ok(agendar(f"{SAB}T11:30"), 201)
    ok(agendar(f"{SAB}T11:45"), 422)
    ok(agendar(f"{SAB}T13:00"), 422)
    ok(agendar(f"{DOM}T10:00"), 422)


def test_conflito_mesmo_veterinario(agendar, novo_vet):
    vid = novo_vet()["id"]
    ok(agendar(f"{SEG}T10:00", vet_id=vid, duracao=60), 201)
    ok(agendar(f"{SEG}T10:00", vet_id=vid), 409)
    ok(agendar(f"{SEG}T10:30", vet_id=vid), 409)
    ok(agendar(f"{SEG}T09:45", vet_id=vid), 409)


def test_horarios_encostados_nao_conflitam(agendar, novo_vet):
    vid = novo_vet()["id"]
    ok(agendar(f"{SEG}T10:00", vet_id=vid), 201)
    ok(agendar(f"{SEG}T10:30", vet_id=vid), 201)
    ok(agendar(f"{SEG}T09:30", vet_id=vid), 201)


def test_veterinarios_diferentes_nao_conflitam(agendar):
    ok(agendar(f"{SEG}T10:00"), 201)
    ok(agendar(f"{SEG}T10:00"), 201)


def test_listagem_filtrada_e_ordenada(api, agendar, novo_vet):
    vid = novo_vet()["id"]
    a1 = ok(agendar(f"{SEG}T14:00", vet_id=vid), 201)
    a2 = ok(agendar(f"{SEG}T09:00", vet_id=vid), 201)
    ok(agendar(f"{TER}T09:00", vet_id=vid), 201)
    ok(agendar(f"{SEG}T11:00"), 201)  # outro veterinário
    lst = ok(api.get("/agendamentos", params={"veterinario_id": vid, "data": SEG}), 200)
    assert [x["id"] for x in lst] == [a2["id"], a1["id"]]
    todos_do_vet = ok(api.get("/agendamentos", params={"veterinario_id": vid}), 200)
    assert len(todos_do_vet) == 3
    inicios = [x["inicio"] for x in todos_do_vet]
    assert inicios == sorted(inicios)


def test_cancelamento_com_antecedencia(api, agendar):
    a = ok(agendar(f"{TER}T10:00"), 201)
    c = ok(api.post(f"/agendamentos/{a['id']}/cancelar", json={"momento": f"{SEG}T10:00"}), 200)
    assert c["status"] == "cancelado"


def test_cancelamento_tardio(api, agendar):
    a = ok(agendar(f"{TER}T10:00"), 201)
    c = ok(api.post(f"/agendamentos/{a['id']}/cancelar", json={"momento": f"{SEG}T10:01"}), 200)
    assert c["status"] == "cancelado_tardio"


def test_cancelamento_sem_corpo_usa_agora(api, agendar):
    a = ok(agendar(f"{TER}T10:00"), 201)
    assert ok(api.post(f"/agendamentos/{a['id']}/cancelar"), 200)["status"] == "cancelado"


def test_cancelar_duas_vezes_e_inexistente(api, agendar):
    a = ok(agendar(f"{TER}T10:00"), 201)
    ok(api.post(f"/agendamentos/{a['id']}/cancelar", json={"momento": f"{SEG}T08:00"}), 200)
    ok(api.post(f"/agendamentos/{a['id']}/cancelar", json={"momento": f"{SEG}T08:00"}), 409)
    ok(api.post("/agendamentos/999999/cancelar"), 404)


def test_cancelado_libera_horario(api, agendar, novo_vet):
    vid = novo_vet()["id"]
    a = ok(agendar(f"{TER}T15:00", vet_id=vid), 201)
    ok(api.post(f"/agendamentos/{a['id']}/cancelar", json={"momento": f"{SEG}T08:00"}), 200)
    ok(agendar(f"{TER}T15:00", vet_id=vid), 201)
