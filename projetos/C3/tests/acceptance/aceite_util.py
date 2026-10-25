"""Constantes e helpers da suíte de aceitação."""
import os

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")

# Datas fixas no futuro. 2030-03-04 é uma segunda-feira.
SEG = "2030-03-04"
TER = "2030-03-05"
SAB = "2030-03-09"
DOM = "2030-03-10"


def ok(resp, status):
    assert resp.status_code == status, f"esperado {status}, veio {resp.status_code}: {resp.text}"
    return resp.json() if resp.content else None
