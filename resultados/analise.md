# Análise do estudo

Execuções registradas: 120

## Projetos base

| Projeto | Arquivos .py | Linhas | Caracteres | Tokens estimados (chars/3,5) |
| --- | --- | --- | --- | --- |
| C1 humano | 39 | 1745 | 60.427 | ~17.265 |
| C2 IA c/ instruções | 1 | 377 | 11.610 | ~3.317 |
| C3 IA livre | 10 | 559 | 17.531 | ~5.009 |

Doc de C1: 20.161 caracteres (~5.760 tokens)

Doc de C2: 9.127 caracteres (~2.608 tokens)

Doc de C3: 7.951 caracteres (~2.272 tokens)

## Tarefa T1

| Condição | n | Sucesso | Tokens entrada (mediana, IQR) | Tokens saída | Turnos | Tempo (s) | Custo ref. (US$) | Linhas alteradas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 humano, sem doc | 5 | 5/5 | 181.512 (161.096–256.314) | 7.127 (7.076–7.768) | 6 (6–8) | 50 (49–55) | 0.213 | 278 (274–280) |
| C2 IA c/ instruções, sem doc | 5 | 5/5 | 90.237 (90.102–161.773) | 2.739 (2.570–3.194) | 4 (4–6) | 24 (23–35) | 0.109 | 60 (60–61) |
| C3 IA livre, sem doc | 5 | 5/5 | 111.792 (88.216–134.652) | 2.788 (2.690–3.558) | 5 (4–6) | 24 (23–33) | 0.105 | 95 (95–100) |
| C1 humano, com doc | 5 | 5/5 | 224.120 (160.550–269.234) | 7.318 (6.921–8.302) | 6 (4–7) | 53 (47–73) | 0.227 | 274 (266–280) |
| C2 IA c/ instruções, com doc | 5 | 5/5 | 110.100 (81.172–112.004) | 2.739 (2.340–3.019) | 4 (3–4) | 26 (22–31) | 0.122 | 58 (54–58) |
| C3 IA livre, com doc | 5 | 5/5 | 106.563 (106.082–109.730) | 4.506 (4.168–4.568) | 12 (10–12) | 37 (34–45) | 0.136 | 98 (95–106) |

**Estilos comparados sem documentação**

Kruskal-Wallis (tokens de entrada): H = 6.86, p = 0.032.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | +0.76 (grande) | +1.00 (grande) | +0.64 (grande) |
| C1 vs C3 | +0.92 (grande) | +1.00 (grande) | +0.76 (grande) |
| C2 vs C3 | +0.20 (pequeno) | -0.28 (pequeno) | -0.12 (desprezível) |

**Estilos comparados com documentação**

Kruskal-Wallis (tokens de entrada): H = 9.42, p = 0.009.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | +1.00 (grande) | +1.00 (grande) | +0.80 (grande) |
| C1 vs C3 | +1.00 (grande) | +1.00 (grande) | -0.96 (grande) |
| C2 vs C3 | +0.12 (desprezível) | -1.00 (grande) | -1.00 (grande) |

**Efeito da documentação (com doc vs sem doc, por estilo)**

| Estilo | Sucesso sem → com | Mediana tokens entrada sem → com | Variação | Cliff's delta (tokens de entrada) |
| --- | --- | --- | --- | --- |
| C1 humano | 5/5 → 5/5 | 181.512 → 224.120 | +23% | +0.20 (pequeno) |
| C2 IA c/ instruções | 5/5 → 5/5 | 90.237 → 110.100 | +22% | -0.28 (pequeno) |
| C3 IA livre | 5/5 → 5/5 | 111.792 → 106.563 | -5% | -0.20 (pequeno) |

Delta positivo = com doc gastou mais.

## Tarefa T3

| Condição | n | Sucesso | Tokens entrada (mediana, IQR) | Tokens saída | Turnos | Tempo (s) | Custo ref. (US$) | Linhas alteradas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 humano, sem doc | 5 | 5/5 | 228.359 (206.554–251.712) | 5.869 (5.640–6.330) | 7 (6–8) | 47 (43–50) | 0.203 | 126 (118–128) |
| C2 IA c/ instruções, sem doc | 5 | 5/5 | 92.653 (91.027–93.986) | 2.035 (1.906–2.202) | 4 (4–4) | 21 (19–25) | 0.104 | 37 (36–38) |
| C3 IA livre, sem doc | 5 | 5/5 | 94.851 (93.709–104.082) | 2.725 (2.566–2.780) | 4 (4–4) | 24 (22–26) | 0.111 | 42 (42–48) |
| C1 humano, com doc | 5 | 5/5 | 233.081 (174.356–236.614) | 6.220 (5.532–7.126) | 6 (4–6) | 52 (44–55) | 0.230 | 112 (108–134) |
| C2 IA c/ instruções, com doc | 5 | 5/5 | 80.657 (80.556–96.014) | 2.215 (2.153–2.608) | 3 (3–4) | 21 (20–31) | 0.112 | 38 (38–40) |
| C3 IA livre, com doc | 5 | 5/5 | 78.911 (78.656–108.270) | 2.966 (2.759–3.391) | 6 (6–7) | 30 (25–33) | 0.119 | 40 (40–42) |

**Estilos comparados sem documentação**

Kruskal-Wallis (tokens de entrada): H = 10.82, p = 0.004.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | +1.00 (grande) | +1.00 (grande) | +1.00 (grande) |
| C1 vs C3 | +1.00 (grande) | +1.00 (grande) | +1.00 (grande) |
| C2 vs C3 | -0.68 (grande) | -1.00 (grande) | -0.20 (pequeno) |

**Estilos comparados com documentação**

Kruskal-Wallis (tokens de entrada): H = 9.78, p = 0.008.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | +1.00 (grande) | +1.00 (grande) | +0.96 (grande) |
| C1 vs C3 | +1.00 (grande) | +1.00 (grande) | -0.64 (grande) |
| C2 vs C3 | +0.36 (médio) | -0.84 (grande) | -1.00 (grande) |

**Efeito da documentação (com doc vs sem doc, por estilo)**

| Estilo | Sucesso sem → com | Mediana tokens entrada sem → com | Variação | Cliff's delta (tokens de entrada) |
| --- | --- | --- | --- | --- |
| C1 humano | 5/5 → 5/5 | 228.359 → 233.081 | +2% | -0.20 (pequeno) |
| C2 IA c/ instruções | 5/5 → 5/5 | 92.653 → 80.657 | -13% | -0.60 (grande) |
| C3 IA livre | 5/5 → 5/5 | 94.851 → 78.911 | -17% | -0.36 (médio) |

Delta positivo = com doc gastou mais.

## Tarefa T4

| Condição | n | Sucesso | Tokens entrada (mediana, IQR) | Tokens saída | Turnos | Tempo (s) | Custo ref. (US$) | Linhas alteradas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 humano, sem doc | 5 | 5/5 | 75.184 (74.464–75.616) | 854 (773–898) | 6 (5–6) | 16 (13–18) | 0.059 | 2 (2–2) |
| C2 IA c/ instruções, sem doc | 5 | 5/5 | 94.142 (73.706–94.669) | 850 (686–1.008) | 6 (4–7) | 14 (12–15) | 0.060 | 2 (2–2) |
| C3 IA livre, sem doc | 5 | 5/5 | 75.893 (74.446–86.780) | 778 (706–820) | 5 (4–6) | 14 (13–17) | 0.058 | 2 (2–2) |
| C1 humano, com doc | 5 | 5/5 | 83.721 (82.085–97.389) | 729 (652–764) | 4 (4–4) | 12 (11–13) | 0.092 | 2 (2–2) |
| C2 IA c/ instruções, com doc | 5 | 5/5 | 67.346 (67.302–67.379) | 672 (635–690) | 4 (4–4) | 12 (10–14) | 0.067 | 2 (2–2) |
| C3 IA livre, com doc | 5 | 5/5 | 67.341 (67.262–67.350) | 618 (608–633) | 4 (4–4) | 12 (10–15) | 0.067 | 2 (2–2) |

**Estilos comparados sem documentação**

Kruskal-Wallis (tokens de entrada): H = 0.78, p = 0.677.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | -0.20 (pequeno) | +0.04 (desprezível) | -0.08 (desprezível) |
| C1 vs C3 | -0.36 (médio) | +0.68 (grande) | +0.28 (pequeno) |
| C2 vs C3 | -0.04 (desprezível) | +0.28 (pequeno) | +0.20 (pequeno) |

**Estilos comparados com documentação**

Kruskal-Wallis (tokens de entrada): H = 9.50, p = 0.009.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | +1.00 (grande) | +0.44 (médio) | +0.20 (pequeno) |
| C1 vs C3 | +1.00 (grande) | +0.84 (grande) | +0.20 (pequeno) |
| C2 vs C3 | +0.20 (pequeno) | +0.84 (grande) | +0.00 (desprezível) |

**Efeito da documentação (com doc vs sem doc, por estilo)**

| Estilo | Sucesso sem → com | Mediana tokens entrada sem → com | Variação | Cliff's delta (tokens de entrada) |
| --- | --- | --- | --- | --- |
| C1 humano | 5/5 → 5/5 | 75.184 → 83.721 | +11% | +1.00 (grande) |
| C2 IA c/ instruções | 5/5 → 5/5 | 94.142 → 67.346 | -28% | -1.00 (grande) |
| C3 IA livre | 5/5 → 5/5 | 75.893 → 67.341 | -11% | -1.00 (grande) |

Delta positivo = com doc gastou mais.

## Tarefa T5

| Condição | n | Sucesso | Tokens entrada (mediana, IQR) | Tokens saída | Turnos | Tempo (s) | Custo ref. (US$) | Linhas alteradas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 humano, sem doc | 5 | 5/5 | 122.090 (118.070–126.794) | 2.453 (2.110–2.587) | 6 (6–8) | 25 (22–25) | 0.118 | 32 (30–36) |
| C2 IA c/ instruções, sem doc | 5 | 5/5 | 86.600 (84.744–88.022) | 1.349 (1.187–1.446) | 7 (4–7) | 15 (14–16) | 0.087 | 9 (8–10) |
| C3 IA livre, sem doc | 5 | 5/5 | 107.830 (103.037–109.242) | 1.522 (1.376–1.596) | 8 (6–8) | 20 (18–20) | 0.086 | 9 (8–11) |
| C1 humano, com doc | 5 | 5/5 | 129.914 (112.506–134.034) | 2.053 (2.024–2.150) | 6 (4–6) | 21 (19–25) | 0.139 | 29 (28–30) |
| C2 IA c/ instruções, com doc | 5 | 5/5 | 94.624 (93.718–118.418) | 1.364 (1.296–1.466) | 6 (4–6) | 17 (16–19) | 0.084 | 11 (8–11) |
| C3 IA livre, com doc | 5 | 5/5 | 98.913 (75.840–100.801) | 1.697 (1.502–1.845) | 5 (5–6) | 19 (17–21) | 0.096 | 11 (10–12) |

**Estilos comparados sem documentação**

Kruskal-Wallis (tokens de entrada): H = 12.50, p = 0.002.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | +1.00 (grande) | +1.00 (grande) | +0.24 (pequeno) |
| C1 vs C3 | +1.00 (grande) | +1.00 (grande) | -0.04 (desprezível) |
| C2 vs C3 | -1.00 (grande) | -0.68 (grande) | -0.48 (grande) |

**Estilos comparados com documentação**

Kruskal-Wallis (tokens de entrada): H = 6.18, p = 0.046.

| Comparação | Cliff's delta (tokens de entrada) | Cliff's delta (tokens de saída) | Cliff's delta (turnos) |
| --- | --- | --- | --- |
| C1 vs C2 | +0.84 (grande) | +1.00 (grande) | +0.20 (pequeno) |
| C1 vs C3 | +0.76 (grande) | +1.00 (grande) | +0.12 (desprezível) |
| C2 vs C3 | +0.28 (pequeno) | -0.84 (grande) | -0.04 (desprezível) |

**Efeito da documentação (com doc vs sem doc, por estilo)**

| Estilo | Sucesso sem → com | Mediana tokens entrada sem → com | Variação | Cliff's delta (tokens de entrada) |
| --- | --- | --- | --- | --- |
| C1 humano | 5/5 → 5/5 | 122.090 → 129.914 | +6% | +0.52 (grande) |
| C2 IA c/ instruções | 5/5 → 5/5 | 86.600 → 94.624 | +9% | +1.00 (grande) |
| C3 IA livre | 5/5 → 5/5 | 107.830 → 98.913 | -8% | -1.00 (grande) |

Delta positivo = com doc gastou mais.

Cliff's delta: positivo = o primeiro grupo gastou mais; |d| < 0,15 desprezível, < 0,33 pequeno, < 0,47 médio, acima disso grande. Ele mede a consistência da diferença, não o tamanho: compare sempre com as medianas.

## Uso de ferramentas (soma por condição e tarefa)

| Tarefa | Condição | Bash | Edit | Grep | Read | Write |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | C1 humano, sem doc | 28 | 0 | 0 | 0 | 0 |
| T1 | C2 IA c/ instruções, sem doc | 20 | 0 | 0 | 0 | 0 |
| T1 | C3 IA livre, sem doc | 19 | 0 | 0 | 0 | 0 |
| T1 | C1 humano, com doc | 24 | 0 | 0 | 0 | 0 |
| T1 | C2 IA c/ instruções, com doc | 8 | 0 | 1 | 5 | 0 |
| T1 | C3 IA livre, com doc | 6 | 18 | 2 | 21 | 4 |
| T3 | C1 humano, sem doc | 31 | 0 | 0 | 0 | 0 |
| T3 | C2 IA c/ instruções, sem doc | 15 | 0 | 0 | 0 | 0 |
| T3 | C3 IA livre, sem doc | 16 | 0 | 0 | 0 | 0 |
| T3 | C1 humano, com doc | 22 | 0 | 0 | 0 | 0 |
| T3 | C2 IA c/ instruções, com doc | 6 | 0 | 0 | 5 | 0 |
| T3 | C3 IA livre, com doc | 7 | 0 | 0 | 20 | 0 |
| T4 | C1 humano, sem doc | 5 | 5 | 5 | 8 | 0 |
| T4 | C2 IA c/ instruções, sem doc | 8 | 2 | 8 | 5 | 0 |
| T4 | C3 IA livre, sem doc | 7 | 4 | 5 | 5 | 0 |
| T4 | C1 humano, com doc | 5 | 5 | 5 | 1 | 0 |
| T4 | C2 IA c/ instruções, com doc | 5 | 5 | 5 | 0 | 0 |
| T4 | C3 IA livre, com doc | 5 | 5 | 5 | 0 | 0 |
| T5 | C1 humano, sem doc | 17 | 0 | 4 | 8 | 0 |
| T5 | C2 IA c/ instruções, sem doc | 10 | 6 | 5 | 4 | 0 |
| T5 | C3 IA livre, sem doc | 20 | 0 | 3 | 7 | 0 |
| T5 | C1 humano, com doc | 12 | 0 | 0 | 11 | 0 |
| T5 | C2 IA c/ instruções, com doc | 8 | 6 | 4 | 3 | 0 |
| T5 | C3 IA livre, com doc | 6 | 3 | 2 | 12 | 0 |
