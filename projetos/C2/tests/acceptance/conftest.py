"""Fixtures da suíte de aceitação. Os testes falam com a API só via HTTP."""
import uuid

import httpx
import pytest

from aceite_util import BASE_URL, ok


@pytest.fixture(scope="session")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        yield client


@pytest.fixture
def novo_tutor(api):
    def _criar(**extra):
        body = {"nome": "Maria Souza", "email": f"maria{uuid.uuid4().hex[:6]}@ex.com", "telefone": "46999990000"}
        body.update(extra)
        return ok(api.post("/tutores", json=body), 201)
    return _criar


@pytest.fixture
def novo_pet(api, novo_tutor):
    def _criar(tutor_id=None, **extra):
        if tutor_id is None:
            tutor_id = novo_tutor()["id"]
        body = {"nome": "Rex", "especie": "cao", "tutor_id": tutor_id, "data_nascimento": "2020-05-01"}
        body.update(extra)
        return ok(api.post("/pets", json=body), 201)
    return _criar


@pytest.fixture
def novo_vet(api):
    def _criar():
        body = {"nome": "Dra. Ana", "crmv": f"PR-{uuid.uuid4().hex[:8]}"}
        return ok(api.post("/veterinarios", json=body), 201)
    return _criar


@pytest.fixture
def novo_produto(api):
    def _criar(**extra):
        body = {"nome": "Vermífugo", "preco_centavos": 2500, "estoque": 10, "estoque_minimo": 2}
        body.update(extra)
        return ok(api.post("/produtos", json=body), 201)
    return _criar


@pytest.fixture
def agendar(api, novo_pet, novo_vet):
    """Cria um agendamento. Retorna a resposta (não verifica status)."""
    def _agendar(inicio, vet_id=None, pet_id=None, duracao=None):
        body = {
            "pet_id": pet_id if pet_id is not None else novo_pet()["id"],
            "veterinario_id": vet_id if vet_id is not None else novo_vet()["id"],
            "inicio": inicio,
        }
        if duracao is not None:
            body["duracao_minutos"] = duracao
        return api.post("/agendamentos", json=body)
    return _agendar
