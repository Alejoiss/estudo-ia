#!/usr/bin/env bash
# Sobe a API. Porta: $PORT (padrão 8000). Banco: $DB_PATH (padrão vetclinic.db).
# NÃO ALTERE ESTE ARQUIVO.
set -e
cd "$(dirname "$0")"
exec python3 -m uvicorn main:app --host 127.0.0.1 --port "${PORT:-8000}"
