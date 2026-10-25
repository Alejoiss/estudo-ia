#!/usr/bin/env bash
# Sobe o servidor com um banco temporário vazio, roda os testes e derruba o servidor.
# Uso: ./test.sh                      -> roda todos os testes em tests/
#      ./test.sh tests/acceptance     -> roda só uma pasta ou arquivo
# NÃO ALTERE ESTE ARQUIVO.
cd "$(dirname "$0")"
PORT="${TEST_PORT:-8765}"
DB="$(mktemp -u /tmp/vetclinic-XXXXXX.db)"
DB_PATH="$DB" PORT="$PORT" ./run.sh > .server.log 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null; wait $PID 2>/dev/null; rm -f "$DB"' EXIT
for _ in $(seq 1 75); do
  python3 -c "import socket;socket.create_connection(('127.0.0.1',$PORT),0.3)" 2>/dev/null && break
  if ! kill -0 $PID 2>/dev/null; then
    echo "ERRO: o servidor nao subiu. Log:"; cat .server.log; exit 1
  fi
  sleep 0.2
done
BASE_URL="http://127.0.0.1:$PORT" python3 -m pytest -q -p no:cacheprovider "${@:-tests}"
