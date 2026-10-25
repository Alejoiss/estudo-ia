#!/usr/bin/env python3
"""Lê resultados/results.jsonl e gera as tabelas do relatório.

Uso (em ~/estudo-ia):  python3 analisar.py
Saídas: resultados/analise.md (tabelas legíveis) e resultados/resumo.csv (para planilha).
Não precisa de bibliotecas extras.
"""
import csv
import json
import math
import random
import statistics
import subprocess
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
RES = RAIZ / "resultados"
ESTILOS = ["C1", "C2", "C3"]
NOMES = {"C1": "C1 humano", "C2": "C2 IA c/ instruções", "C3": "C3 IA livre"}
random.seed(42)


def carregar():
    linhas = [json.loads(l) for l in (RES / "results.jsonl").read_text().splitlines() if l.strip()]
    for r in linhas:
        # agente alterou código sem usar Edit/Write (ex.: sed no Bash); nesses casos a métrica de exploração é imprecisa
        r["edicao_via_bash"] = r.get("ferramentas", {}).get("Edit", 0) + r.get("ferramentas", {}).get("Write", 0) == 0 \
            and r.get("linhas_adicionadas", 0) + r.get("linhas_removidas", 0) > 0
    return linhas


def mediana_iqr(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return "–"
    if len(xs) < 4:
        return f"{statistics.median(xs):,.0f} ({min(xs):,.0f}–{max(xs):,.0f})".replace(",", ".")
    q = statistics.quantiles(xs, n=4)
    return f"{statistics.median(xs):,.0f} ({q[0]:,.0f}–{q[2]:,.0f})".replace(",", ".")


def ic_mediana(xs, n_boot=10000):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None
    meds = sorted(statistics.median(random.choices(xs, k=len(xs))) for _ in range(n_boot))
    return meds[int(0.025 * n_boot)], meds[int(0.975 * n_boot)]


def cliffs_delta(a, b):
    """Tamanho de efeito: P(a>b) - P(a<b). -1 a 1; |d|<0.15 desprezível, <0.33 pequeno, <0.47 médio, senão grande."""
    if not a or not b:
        return None
    maior = sum(1 for x in a for y in b if x > y)
    menor = sum(1 for x in a for y in b if x < y)
    return (maior - menor) / (len(a) * len(b))


def rotulo_delta(d):
    if d is None:
        return "–"
    m = abs(d)
    t = "desprezível" if m < 0.15 else "pequeno" if m < 0.33 else "médio" if m < 0.47 else "grande"
    return f"{d:+.2f} ({t})"


def kruskal_wallis(grupos):
    """Kruskal-Wallis com correção de empates; p exato da qui-quadrado só para 3 grupos (gl=2)."""
    grupos = [g for g in grupos if g]
    if len(grupos) != 3:
        return None, None
    todos = sorted((x, i) for i, g in enumerate(grupos) for x in g)
    n = len(todos)
    postos = [0.0] * n
    i = 0
    empates = 0
    while i < n:
        j = i
        while j + 1 < n and todos[j + 1][0] == todos[i][0]:
            j += 1
        for k in range(i, j + 1):
            postos[k] = (i + j) / 2 + 1
        t = j - i + 1
        empates += t ** 3 - t
        i = j + 1
    soma = [0.0] * 3
    for (x, g), p in zip(todos, postos):
        soma[g] += p
    h = 12 / (n * (n + 1)) * sum(soma[g] ** 2 / len(grupos[g]) for g in range(3)) - 3 * (n + 1)
    c = 1 - empates / (n ** 3 - n) if n > 1 else 1
    h = h / c if c else 0
    return h, math.exp(-h / 2)


def tamanho_projetos():
    linhas = []
    for e in ESTILOS:
        r = subprocess.run(f"git -C projetos/{e} archive base | tar -t", cwd=RAIZ, shell=True,
                           capture_output=True, text=True)
        arquivos = [a for a in r.stdout.split() if a.endswith(".py") and not a.startswith("tests/")]
        chars = n_linhas = 0
        for a in arquivos:
            s = subprocess.run(f"git -C projetos/{e} show base:{a}", cwd=RAIZ, shell=True,
                               capture_output=True, text=True).stdout
            chars += len(s)
            n_linhas += s.count("\n")
        linhas.append((e, len(arquivos), n_linhas, chars, round(chars / 3.5)))
    return linhas


def rotulo(e, d):
    return f"{NOMES[e]}, {'com doc' if d else 'sem doc'}"


def main():
    dados = carregar()
    tarefas = sorted({r["tarefa"] for r in dados})
    docs = sorted({r["doc"] for r in dados})
    md = ["# Análise do estudo\n", f"Execuções registradas: {len(dados)}\n"]

    md.append("## Projetos base\n")
    md.append("| Projeto | Arquivos .py | Linhas | Caracteres | Tokens estimados (chars/3,5) |")
    md.append("| --- | --- | --- | --- | --- |")
    for e, a, l, c, t in tamanho_projetos():
        md.append(f"| {NOMES[e]} | {a} | {l} | {c:,} | ~{t:,} |".replace(",", "."))
    for e in ESTILOS:
        doc = RAIZ / "docs" / f"{e}.md"
        if doc.exists():
            c = len(doc.read_text())
            md.append(f"\nDoc de {e}: {c:,} caracteres (~{round(c / 3.5):,} tokens)".replace(",", "."))
    md.append("")

    csv_linhas = []
    for t in tarefas:
        md.append(f"## Tarefa {t}\n")
        md.append("| Condição | n | Sucesso | Tokens entrada (mediana, IQR) | Tokens saída | Turnos | Tempo (s) | "
                  "Custo ref. (US$) | Linhas alteradas |")
        md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        grupo = {}
        for d in docs:
            for e in ESTILOS:
                rs = [r for r in dados if r["tarefa"] == t and r["estilo"] == e and r["doc"] == d]
                grupo[(e, d)] = rs
                if not rs:
                    continue
                ok = sum(r["sucesso"] for r in rs)
                ent = [r["tokens_entrada_total"] for r in rs]
                custo = statistics.median([r["custo_ref_usd"] or 0 for r in rs])
                md.append(f"| {rotulo(e, d)} | {len(rs)} | {ok}/{len(rs)} | {mediana_iqr(ent)} | "
                          f"{mediana_iqr([r['tokens_saida'] for r in rs])} | {mediana_iqr([r['turnos'] for r in rs])} | "
                          f"{mediana_iqr([(r['duracao_ms'] or 0) / 1000 for r in rs])} | {custo:.3f} | "
                          f"{mediana_iqr([r['linhas_adicionadas'] + r['linhas_removidas'] for r in rs])} |")
                ic = ic_mediana(ent)
                custo_total = sum(r["custo_ref_usd"] or 0 for r in rs)
                csv_linhas.append({
                    "tarefa": t, "estilo": e, "doc": d, "n": len(rs), "sucessos": ok,
                    "tokens_entrada_mediana": statistics.median(ent),
                    "tokens_entrada_ic95_inf": ic[0] if ic else "", "tokens_entrada_ic95_sup": ic[1] if ic else "",
                    "tokens_saida_mediana": statistics.median([r["tokens_saida"] for r in rs]),
                    "turnos_mediana": statistics.median([r["turnos"] for r in rs]),
                    "custo_ref_mediana": round(custo, 4),
                    "custo_ref_por_sucesso": round(custo_total / ok, 4) if ok else "",
                    "edicoes_via_bash": sum(r["edicao_via_bash"] for r in rs),
                })
        md.append("")

        for d in docs:
            grupos = [[r["tokens_entrada_total"] for r in grupo[(e, d)]] for e in ESTILOS]
            h, p = kruskal_wallis(grupos)
            md.append(f"**Estilos comparados {'com' if d else 'sem'} documentação**\n")
            if h is not None:
                md.append(f"Kruskal-Wallis (tokens de entrada): H = {h:.2f}, p = {p:.3f}.\n")
            md.append("| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |")
            md.append("| --- | --- | --- | --- |")
            for a, b in combinations(ESTILOS, 2):
                ga, gb = grupo[(a, d)], grupo[(b, d)]
                md.append(f"| {a} vs {b} | "
                          + " | ".join(rotulo_delta(cliffs_delta([r[k] for r in ga], [r[k] for r in gb]))
                                       for k in ("tokens_entrada_total", "tokens_saida", "turnos")) + " |")
            md.append("")

        if len(docs) == 2:
            md.append("**Efeito da documentação (com doc vs sem doc, por estilo)**\n")
            md.append("| Estilo | Sucesso sem → com | Mediana tokens entrada sem → com | Variação | Cliff's delta (tokens de entrada) |")
            md.append("| --- | --- | --- | --- | --- |")
            for e in ESTILOS:
                sem, com = grupo[(e, False)], grupo[(e, True)]
                if not sem or not com:
                    continue
                ms = statistics.median([r["tokens_entrada_total"] for r in sem])
                mc = statistics.median([r["tokens_entrada_total"] for r in com])
                md.append(f"| {NOMES[e]} | {sum(r['sucesso'] for r in sem)}/{len(sem)} → "
                          f"{sum(r['sucesso'] for r in com)}/{len(com)} | {ms:,.0f} → {mc:,.0f} | "
                          f"{(mc - ms) / ms:+.0%} | ".replace(",", ".")
                          + rotulo_delta(cliffs_delta([r["tokens_entrada_total"] for r in com],
                                                      [r["tokens_entrada_total"] for r in sem])) + " |")
            md.append("\nDelta positivo = com doc gastou mais.\n")

        falhas = [r for r in dados if r["tarefa"] == t and not r["sucesso"]]
        if falhas:
            md.append("Execuções sem sucesso:\n")
            for r in falhas:
                md.append(f"- {r['id']}: ocultos {r['ocultos_passou']}/{r['ocultos_total']}, regressão "
                          f"{r['regressao_passou']}/{r['regressao_total']}, falhando: {', '.join(r['testes_falhando'][:5])}")
            md.append("")

    md.append("Cliff's delta: positivo = o primeiro grupo gastou mais; |d| < 0,15 desprezível, < 0,33 pequeno, "
              "< 0,47 médio, acima disso grande. Ele mede a consistência da diferença, não o tamanho: "
              "compare sempre com as medianas.\n")

    md.append("## Uso de ferramentas (soma por condição e tarefa)\n")
    nomes_ferr = sorted({f for r in dados for f in r.get("ferramentas", {})})
    md.append("| Tarefa | Condição | " + " | ".join(nomes_ferr) + " |")
    md.append("| --- | --- | " + " | ".join("---" for _ in nomes_ferr) + " |")
    for t in tarefas:
        for d in docs:
            for e in ESTILOS:
                rs = [r for r in dados if r["tarefa"] == t and r["estilo"] == e and r["doc"] == d]
                if rs:
                    md.append(f"| {t} | {rotulo(e, d)} | " + " | ".join(
                        str(sum(r.get("ferramentas", {}).get(f, 0) for r in rs)) for f in nomes_ferr) + " |")

    (RES / "analise.md").write_text("\n".join(md) + "\n")
    with open(RES / "resumo.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_linhas[0].keys()) if csv_linhas else ["vazio"])
        w.writeheader()
        w.writerows(csv_linhas)
    print((RES / "analise.md").read_text())


if __name__ == "__main__":
    main()
