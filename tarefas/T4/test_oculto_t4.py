"""Testes ocultos da tarefa T4 (bug de horários encostados). Não são vistos pelo agente."""
from aceite_util import SEG, TER, ok


def test_t4_encostado_depois(agendar, novo_vet):
    vid = novo_vet()["id"]
    ok(agendar(f"{SEG}T10:00", vet_id=vid), 201)
    ok(agendar(f"{SEG}T10:30", vet_id=vid), 201)


def test_t4_encostado_antes(agendar, novo_vet):
    vid = novo_vet()["id"]
    ok(agendar(f"{SEG}T10:00", vet_id=vid), 201)
    ok(agendar(f"{SEG}T09:30", vet_id=vid), 201)


def test_t4_duracoes_diferentes(agendar, novo_vet):
    vid = novo_vet()["id"]
    ok(agendar(f"{TER}T14:00", vet_id=vid, duracao=60), 201)
    ok(agendar(f"{TER}T15:00", vet_id=vid, duracao=45), 201)
    ok(agendar(f"{TER}T13:15", vet_id=vid, duracao=45), 201)
    ok(agendar(f"{TER}T14:45", vet_id=vid), 409)
    ok(agendar(f"{TER}T13:00", vet_id=vid, duracao=30), 409)  # termina 13:30, sobrepõe 13:15-14:00


def test_t4_sobreposicao_continua_bloqueada(agendar, novo_vet):
    vid = novo_vet()["id"]
    ok(agendar(f"{SEG}T15:00", vet_id=vid, duracao=60), 201)
    ok(agendar(f"{SEG}T15:00", vet_id=vid), 409)
    ok(agendar(f"{SEG}T15:30", vet_id=vid), 409)
    ok(agendar(f"{SEG}T14:45", vet_id=vid), 409)
