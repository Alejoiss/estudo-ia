#!/usr/bin/env python3
"""Executa as tarefas do estudo e grava uma linha de métricas por execução.

Uso (dentro de ~/estudo-ia, com a .venv ativada):
    python3 runner.py --piloto            # 1 execução de teste (C2, T4), salva em resultados/piloto.jsonl
    python3 runner.py                     # todas as execuções pendentes do estudo
    python3 runner.py --limite 4          # no máximo 4 execuções nesta rodada
    python3 runner.py --so C1 T1          # só as execuções de um estilo e uma tarefa

O script pode ser interrompido e rodado de novo: execuções já registradas são puladas.
Se o limite de uso do plano for atingido, ele para sem registrar a execução incompleta.
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
KIT = RAIZ / "kit"
PROJETOS = RAIZ / "projetos"
TAREFAS = RAIZ / "tarefas"
DOCS = RAIZ / "docs"
RESULTADOS = RAIZ / "resultados"

ESTILOS = ["C1", "C2", "C3"]
TAREFAS_ESTUDO = ["T1", "T3", "T4", "T5"]
DOC = [False, True]    # True usa docs/<estilo>.md como CLAUDE.md do projeto
REPETICOES = 5
MODELO = "sonnet"
MAX_TURNOS = 80
TIMEOUT_S = 40 * 60
CONFIG_DIR = os.path.expanduser("~/.claude-estudo")
ARQUIVOS_FIXOS = ["SPEC.md", "run.sh", "test.sh", "requirements.txt"]


def sh(cmd, cwd, **kw):
    return subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True, **kw)


def remover_testes(work, arquivo_lista):
    """Remove da suíte de aceitação as funções de teste listadas no arquivo (se existir)."""
    if not arquivo_lista.exists():
        return
    for nome in arquivo_lista.read_text().split():
        for f in (work / "tests" / "acceptance").glob("test_*.py"):
            s = f.read_text()
            m = re.search(rf"\ndef {nome}\(.*?(?=\n\n\ndef |\Z)", s, re.S)
            if m:
                f.write_text(s[: m.start()] + s[m.end():])


def preparar(estilo, tarefa, com_doc, work):
    """Exporta a versão congelada (tag base) e aplica o que a tarefa exige."""
    r = sh(f"git -C '{PROJETOS / estilo}' archive base | tar -x -C '{work}'", RAIZ)
    if r.returncode:
        sys.exit(f"Falha ao exportar {estilo}@base: {r.stderr}")
    shutil.rmtree(work / ".pytest_cache", ignore_errors=True)
    (work / ".server.log").unlink(missing_ok=True)

    bug = TAREFAS / tarefa / "bug.json"
    if bug.exists():
        arq, antigo, novo = json.loads(bug.read_text())[estilo]
        f = work / arq
        s = f.read_text()
        assert s.count(antigo) == 1, f"trecho do bug não encontrado em {f}"
        f.write_text(s.replace(antigo, novo))

    # ocultar.txt: testes escondidos só durante a execução (voltam na avaliação)
    # substitui.txt: testes que a tarefa torna obsoletos (somem da execução e da avaliação)
    remover_testes(work, TAREFAS / tarefa / "ocultar.txt")
    remover_testes(work, TAREFAS / tarefa / "substitui.txt")

    if com_doc:
        shutil.copy(DOCS / f"{estilo}.md", work / "CLAUDE.md")

    sh("git init -q && git add -A && git -c user.name=estudo -c user.email=e@e commit -qm inicio", work)


def rodar_agente(prompt, work, log):
    env = {**os.environ, "CLAUDE_CONFIG_DIR": CONFIG_DIR}
    cmd = [
        "claude", "-p", prompt, "--model", MODELO, "--max-turns", str(MAX_TURNOS),
        "--strict-mcp-config", "--output-format", "stream-json", "--verbose",
        "--allowedTools", "Read,Edit,Write,MultiEdit,Glob,Grep,Bash,TodoWrite",
        "--disallowedTools", "WebFetch,WebSearch,Agent,Task",
    ]
    inicio = time.time()
    try:
        p = subprocess.run(cmd, cwd=work, env=env, text=True, capture_output=True, timeout=TIMEOUT_S)
        saida, erro = p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        saida, erro = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
    log.write_text(saida)
    if erro:
        log.with_suffix(".stderr.txt").write_text(erro)
    eventos = []
    for linha in saida.splitlines():
        try:
            eventos.append(json.loads(linha))
        except json.JSONDecodeError:
            pass
    return eventos, time.time() - inicio, erro


def metricas_agente(eventos):
    init = next((e for e in eventos if e.get("type") == "system" and e.get("subtype") == "init"), {})
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), None)
    ferramentas, arquivos_lidos = {}, set()
    chars_antes_edicao, editou = 0, False
    ids_leitura = set()
    for e in eventos:
        conteudo = (e.get("message") or {}).get("content") or []
        if not isinstance(conteudo, list):
            continue
        for b in conteudo:
            if e.get("type") == "assistant" and b.get("type") == "tool_use":
                nome = b.get("name")
                ferramentas[nome] = ferramentas.get(nome, 0) + 1
                entrada = b.get("input") or {}
                if nome == "Read":
                    arquivos_lidos.add(entrada.get("file_path"))
                if nome in ("Edit", "Write", "MultiEdit"):
                    editou = True
                if not editou:
                    ids_leitura.add(b.get("id"))
            if e.get("type") == "user" and b.get("type") == "tool_result" and b.get("tool_use_id") in ids_leitura:
                c = b.get("content")
                chars_antes_edicao += len(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False))
    uso = (final or {}).get("usage") or {}
    return {
        "modelo": init.get("model"),
        "n_ferramentas_disponiveis": len(init.get("tools") or []),
        "mcp": init.get("mcp_servers"),
        "resultado_subtipo": (final or {}).get("subtype"),
        "erro_agente": (final or {}).get("is_error"),
        "texto_final": ((final or {}).get("result") or "")[:500],
        "custo_ref_usd": (final or {}).get("total_cost_usd"),
        "turnos": (final or {}).get("num_turns"),
        "duracao_ms": (final or {}).get("duration_ms"),
        "tokens_entrada": uso.get("input_tokens"),
        "tokens_cache_criacao": uso.get("cache_creation_input_tokens"),
        "tokens_cache_leitura": uso.get("cache_read_input_tokens"),
        "tokens_saida": uso.get("output_tokens"),
        "tokens_entrada_total": sum(uso.get(k) or 0 for k in
                                    ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "chamadas_ferramenta": sum(ferramentas.values()),
        "ferramentas": ferramentas,
        "arquivos_lidos": len(arquivos_lidos),
        "chars_explorados_antes_de_editar": chars_antes_edicao,
    }, final


def avaliar(estilo, tarefa, work, pasta):
    """Restaura arquivos fixos e testes originais, injeta os ocultos e roda a avaliação."""
    alterados = sh("git status --porcelain -- " + " ".join(ARQUIVOS_FIXOS + ["tests/acceptance"]), work).stdout
    sh("git add -A", work)
    numstat = sh("git diff --cached --numstat HEAD", work).stdout
    (pasta / "diff.patch").write_text(sh("git diff --cached HEAD", work).stdout)

    add = rem = 0
    arquivos_codigo, arquivos_teste = set(), set()
    for linha in numstat.splitlines():
        a, r, nome = linha.split("\t", 2)
        if nome.startswith("tests/") or nome in ARQUIVOS_FIXOS:
            arquivos_teste.add(nome)
            continue
        arquivos_codigo.add(nome)
        add += int(a) if a.isdigit() else 0
        rem += int(r) if r.isdigit() else 0

    for nome in ARQUIVOS_FIXOS:
        shutil.copy(KIT / nome, work / nome)
    shutil.rmtree(work / "tests" / "acceptance")
    shutil.copytree(KIT / "tests" / "acceptance", work / "tests" / "acceptance")
    remover_testes(work, TAREFAS / tarefa / "substitui.txt")
    for f in (TAREFAS / tarefa).glob("test_oculto_*.py"):
        shutil.copy(f, work / "tests" / "acceptance" / f.name)

    sh("pkill -f 'uvicorn main:app'", work)
    junit = pasta / "junit.xml"
    r = sh(f"./test.sh --junitxml='{junit}' tests/acceptance", work, timeout=600)
    (pasta / "avaliacao.txt").write_text(r.stdout + r.stderr)

    ocultos = {"total": 0, "passou": 0}
    regressao = {"total": 0, "passou": 0}
    falhas = []
    if junit.exists():
        for caso in ET.parse(junit).iter("testcase"):
            alvo = ocultos if "test_oculto_" in (caso.get("classname") or "") else regressao
            alvo["total"] += 1
            if caso.find("failure") is None and caso.find("error") is None and caso.find("skipped") is None:
                alvo["passou"] += 1
            else:
                falhas.append(caso.get("name"))
    servidor_subiu = junit.exists()
    return {
        "servidor_subiu": servidor_subiu,
        "ocultos_total": ocultos["total"], "ocultos_passou": ocultos["passou"],
        "regressao_total": regressao["total"], "regressao_passou": regressao["passou"],
        "testes_falhando": falhas,
        "sucesso": servidor_subiu and ocultos["total"] > 0 and ocultos["passou"] == ocultos["total"]
                   and regressao["passou"] == regressao["total"],
        "linhas_adicionadas": add, "linhas_removidas": rem,
        "arquivos_codigo_tocados": len(arquivos_codigo),
        "arquivos_teste_tocados": len(arquivos_teste),
        "alterou_arquivos_proibidos": bool(alterados.strip()),
    }


def limite_atingido(final, erro):
    """True quando a execução não chegou ao fim por motivo externo (limite do plano, falha do CLI).
    Estourar o máximo de turnos NÃO conta: é um resultado legítimo (falha da tarefa)."""
    if final is None:
        return True
    if final.get("subtype") == "error_max_turns" or not final.get("is_error"):
        return False
    texto = (str(final.get("result") or "") + " " + (erro or "")).lower()
    return "limit" in texto or "rate" in texto or "overloaded" in texto


def executar(estilo, tarefa, com_doc, rep, arquivo_saida):
    id_exec = f"{datetime.now():%Y%m%d-%H%M%S}-{estilo}-{tarefa}-{'doc' if com_doc else 'sem'}-r{rep}"
    pasta = RESULTADOS / "execucoes" / id_exec
    pasta.mkdir(parents=True)
    work = Path(tempfile.mkdtemp(prefix="estudo-"))
    try:
        preparar(estilo, tarefa, com_doc, work)
        prompt = (TAREFAS / "preambulo.txt").read_text() + (TAREFAS / tarefa / "prompt.txt").read_text()
        print(f"[{datetime.now():%H:%M:%S}] {id_exec}: agente trabalhando...", flush=True)
        eventos, segundos, erro = rodar_agente(prompt, work, pasta / "agente.jsonl")
        m_agente, final = metricas_agente(eventos)
        if limite_atingido(final, erro):
            print("\nO agente não terminou (provável limite de uso do plano ou erro do CLI).")
            print(f"Detalhes em {pasta}. A execução NÃO foi registrada; rode o script de novo mais tarde.")
            shutil.move(str(pasta), str(pasta) + "-INCOMPLETA")
            return False
        m_aval = avaliar(estilo, tarefa, work, pasta)
        linha = {"id": id_exec, "estilo": estilo, "tarefa": tarefa, "doc": com_doc, "rep": rep,
                 "inicio": datetime.now().isoformat(timespec="seconds"), "segundos_parede": round(segundos, 1),
                 **m_aval, **m_agente}
        with open(arquivo_saida, "a") as out:
            out.write(json.dumps(linha, ensure_ascii=False) + "\n")
        print(f"    sucesso={linha['sucesso']} ocultos={linha['ocultos_passou']}/{linha['ocultos_total']} "
              f"regressao={linha['regressao_passou']}/{linha['regressao_total']} "
              f"tokens_entrada={linha['tokens_entrada_total']} tokens_saida={linha['tokens_saida']} "
              f"turnos={linha['turnos']} custo_ref=${linha['custo_ref_usd']}", flush=True)
        return True
    finally:
        sh("pkill -f 'uvicorn main:app'", RAIZ)
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", action="store_true")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--so", nargs=2, metavar=("ESTILO", "TAREFA"))
    a = ap.parse_args()
    RESULTADOS.mkdir(exist_ok=True)

    if shutil.which("claude") is None:
        sys.exit("Comando 'claude' não encontrado no PATH.")
    if True in DOC:
        faltando = [e for e in ESTILOS if not (DOCS / f"{e}.md").exists()]
        if faltando and not a.piloto:
            sys.exit(f"Faltam as docs em docs/: {', '.join(e + '.md' for e in faltando)}")
    for e in ESTILOS:
        if sh("git rev-parse -q --verify refs/tags/base", PROJETOS / e).returncode:
            sys.exit(f"projetos/{e} não tem a tag 'base'. Congele o projeto antes.")

    if a.piloto:
        executar("C2", "T4", False, 0, RESULTADOS / "piloto.jsonl")
        return

    saida = RESULTADOS / "results.jsonl"
    feitos = set()
    if saida.exists():
        for l in saida.read_text().splitlines():
            r = json.loads(l)
            feitos.add((r["estilo"], r["tarefa"], r["doc"], r["rep"]))
    jobs = [(e, t, d, r) for e in ESTILOS for t in TAREFAS_ESTUDO for d in DOC for r in range(REPETICOES)
            if (e, t, d, r) not in feitos and (not a.so or (e, t) == tuple(a.so))]
    random.shuffle(jobs)
    if a.limite:
        jobs = jobs[: a.limite]
    print(f"{len(feitos)} execuções já registradas; {len(jobs)} nesta rodada.")
    for j in jobs:
        if not executar(*j, saida):
            break
    print("Fim da rodada.")


if __name__ == "__main__":
    main()
