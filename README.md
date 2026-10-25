# Código para humanos vs. código para IA: um estudo com agentes de programação

*Estudo realizado em outubro de 2026.*

## Contexto

Este estudo testa se o código escrito para ser lido por pessoas também é o melhor código para um agente de IA trabalhar, e se documentação ajuda esse agente.

A engenharia de software tradicional otimiza o código para leitores humanos: nomes longos e descritivos, separação em camadas, docstrings, comentários, princípios como SOLID e Clean Code. Essas práticas existem porque pessoas têm memória de trabalho limitada, precisam de pistas para navegar e mantêm o código por anos.

Hoje, uma parte crescente do código é lida e modificada por agentes de IA, e eles têm outras restrições:

- **Pagam por token.** Cada arquivo lido e cada linha escrita custam dinheiro e tempo, e código verboso custa mais.
- **Têm janela de contexto limitada.** Uma funcionalidade espalhada em muitos arquivos obriga o agente a carregar mais contexto para entendê-la.
- **Não precisam das mesmas pistas.** Um modelo lê um identificador curto e consistente sem dificuldade, e pode não precisar de comentários explicando o óbvio.
- **Seguem as convenções que encontram.** Se o projeto é verboso, o código novo que o agente escreve também será.

Daí a hipótese: talvez um projeto escrito *para a IA*, mais denso, com menos arquivos e menos indireção, seja mais barato e igualmente confiável para um agente modificar. A mesma dúvida vale para a documentação: um guia escrito para um desenvolvedor recém-contratado ajuda um agente tanto quanto um mapa denso escrito especificamente para IA?

## Objetivo, perguntas e hipóteses

O objetivo é medir, num experimento controlado, como o estilo do código e a documentação afetam o custo e a taxa de acerto de um agente de IA ao implementar tarefas reais num projeto existente.

**Perguntas:**

1. Um projeto escrito para a IA é mais barato e tão confiável para o agente modificar quanto um projeto escrito segundo boas práticas humanas?
2. É preciso dizer ao modelo *como* escrever para IA, ou ele chega a um bom estilo sozinho quando recebe esse objetivo?
3. A documentação ajuda o agente? E uma doc escrita para IA ajuda mais que uma escrita para humanos?

**Hipóteses, definidas antes de rodar, e o que os dados mostraram:**

| Hipótese | Resultado |
| --- | --- |
| H1: os estilos para IA (C2, C3) custam menos que o estilo humano (C1) | Confirmada nas tarefas que criam ou alteram lógica (1,4 a 2 vezes mais barato); não vale para a correção de um bug localizado, onde houve empate |
| H2: os estilos para IA não têm taxa de sucesso menor | Confirmada: 100% de sucesso em todos os cenários |
| H3: a documentação reduz o esforço do agente | Parcial: reduziu tokens de entrada em algumas combinações, mas aumentou o custo em 11 de 12 |
| H4: a doc para IA ajuda mais que a doc para humanos | Parcial: a doc para IA se saiu melhor que a humana, mas nenhuma das duas compensou o próprio custo neste projeto |

## Desenho do estudo

O mesmo sistema foi implementado três vezes, com comportamento idêntico e estilos diferentes, e cada versão recebeu as mesmas tarefas, com e sem documentação. Só o estilo do código e a presença da doc mudam entre as condições.

| Cenário | Como o código foi escrito | Documentação (quando presente) |
| --- | --- | --- |
| C1, estilo humano | Seguindo PEP 8, Clean Code e SOLID: camadas separadas, nomes longos, type hints, docstrings e comentários | Guia em prosa para um desenvolvedor novo na equipe |
| C2, IA com instruções | Seguindo regras explícitas para minimizar tokens: sem comentários, nomes curtos e consistentes, mínimo de indireção e de arquivos | Arquivo de contexto denso para IA |
| C3, IA livre | O modelo escolheu sozinho o estilo que considerou mais eficiente para um LLM, sem regras dadas | Arquivo de contexto denso para IA |

**O que fica fixo** em todas as condições, para que a comparação seja justa:

- o problema e a especificação (uma API de clínica veterinária);
- a linguagem e as bibliotecas (Python 3.12, FastAPI, SQLite);
- o contrato da API, verificado por 37 testes de aceitação que falam só por HTTP e por isso valem para qualquer estrutura interna;
- o modelo (Claude Sonnet 5.5) e a ferramenta (Claude Code), com configuração limpa;
- o texto de cada tarefa, idêntico palavra por palavra nos três cenários.

**O que é medido:** se a tarefa foi resolvida (testes ocultos que o agente não vê) e quanto custou (tokens de entrada e saída, turnos, tempo e custo de referência). Foram 4 tarefas, em 6 condições (3 estilos × com/sem doc), repetidas 5 vezes cada, num total de 120 execuções. Os detalhes estão em [O que foi feito](#o-que-foi-feito).

## Resultados em resumo

Em 120 execuções, o código no estilo humano custou de **1,4 a 2 vezes mais** para a IA nas tarefas que criam ou alteram lógica, e a documentação, em vez de economizar, **aumentou o custo em 11 de 12 combinações**. A qualidade empatou: as 120 execuções resolveram a tarefa.

- **Estilo:** sem documentação, o custo mediano do C1 (humano) foi 2,0 vezes o do estilo para IA na T1 (cadastro novo), 1,9 vez na T3 (regra transversal) e 1,4 vez na T5 (mudança de regra). Na T4 (bug localizado), os três empataram.
- **C2 e C3 se equivalem:** o modelo, livre para escolher, chegou a um estilo tão barato quanto o guiado por instruções detalhadas.
- **Documentação:** em algumas combinações ela reduziu os tokens de entrada (até −28%), mas o custo subiu quase sempre. A doc humana do C1, a maior, foi a pior: de +7% a +56% no custo, sem reduzir tokens.
- **A doc para IA mudou o comportamento do agente:** ele passou a ir direto ao ponto certo. Na T4 com doc, C2 e C3 ficaram em 67,3 mil tokens de mediana, com a metade central das execuções variando menos de 0,2%.

Os resultados valem para um projeto pequeno e um único modelo (Claude Sonnet 5.5); as limitações estão no fim do relatório.

## O que foi feito

Três projetos com comportamento idêntico foram gerados em estilos diferentes, e o mesmo agente executou quatro tarefas em cada um, com e sem documentação, 5 vezes cada combinação: 3 × 4 × 2 × 5 = 120 execuções automatizadas.

1. **Problema:** API REST de uma clínica veterinária (tutores, pets, veterinários, produtos, agendamentos, atendimentos e faturas), especificada num `SPEC.md` com regras de negócio que se cruzam.
2. **Contrato fixo:** Python 3.12, FastAPI e `sqlite3`, mesmas dependências, `main.py` como ponto de entrada. Uma suíte de 37 testes de aceitação fala com a API só por HTTP, então vale igualmente para os três estilos.
3. **Geração:** cada projeto foi gerado do zero pelo Claude Sonnet 5.5, com prompt idêntico exceto pelo bloco de estilo, até passar nos 37 testes. Depois foi congelado com uma tag git.
   - C1: estilo humano (PEP 8, SOLID, camadas, docstrings).
   - C2: estilo para IA com instruções explícitas (mínimo de tokens e de indireção).
   - C3: a IA escolheu livremente o estilo mais fácil para um LLM.
4. **Tarefas**, cada uma com testes ocultos que o agente não via:
   - T1, cadastro novo: CRUD de vacinas com data de reforço calculada e nova regra de exclusão de pet. 10 testes.
   - T3, regra transversal: plano de fidelidade do tutor com desconto na consulta, aplicado na geração da fatura. 7 testes.
   - T4, correção de bug: o mesmo bug injetado nos três projetos (`<` trocado por `<=` na checagem de conflito de agenda), descrito só por um relato de usuário; o teste que o denunciaria ficou oculto. 4 testes.
   - T5, mudança de regra: cancelamento passa de 24 h para 12 h e cancelamento tardio gera fatura de taxa. O teste antigo da regra de 24 h foi descartado. 5 testes.
5. **Documentação:** gerada pelo mesmo modelo, só com permissão de leitura, depois do código congelado. O C1 recebeu uma doc para humanos (guia de onboarding); C2 e C3, um arquivo de contexto denso para IA. As três foram revisadas contra o código: todos os nomes citados existem. Uma correção foi necessária: a doc do C1 usava "Vacinas" como exemplo de nova entidade, o que entregaria a solução da T1, e o exemplo foi trocado por "Fornecedores". Nas condições com doc, ela entrou como `CLAUDE.md`, que o Claude Code carrega automaticamente.
6. **Execução:** Claude Code em modo não interativo, modelo fixo, configuração limpa (sem memórias, preferências ou MCP do usuário), sem web e sem subagentes, cada execução numa cópia nova da versão congelada, em ordem aleatória.
7. **Avaliação:** sucesso = todos os testes ocultos e toda a suíte de aceitação passando, com arquivos fixos e testes originais restaurados antes de avaliar.

**Métrica principal: custo de referência.** É o valor que o Claude Code calcula a preço de API. Ele pondera cada tipo de token pelo preço: saída é a mais cara, conteúdo novo no contexto custa mais que conteúdo relido do cache. Por isso é uma medida de esforço melhor que a soma simples de tokens, e acompanha o consumo da cota do plano. O estudo rodou numa assinatura Pro, sem gasto real.

## Projetos base

Os três projetos passam nos mesmos 37 testes, mas o C1 tem 3,5 vezes mais código que o C3 e 5,2 vezes mais que o C2. As docs para IA ficaram quase do tamanho do próprio código que descrevem.

| Projeto | Arquivos .py | Linhas | Caracteres de código | Tokens de código (est.) | Caracteres da doc | Tokens da doc (est.) |
| --- | --- | --- | --- | --- | --- | --- |
| C1 humano | 39 | 1.745 | 60.427 | ~17.300 | 20.161 | ~5.800 |
| C2 IA com instruções | 1 | 377 | 11.610 | ~3.300 | 9.127 | ~2.600 |
| C3 IA livre | 10 | 559 | 17.531 | ~5.000 | 7.951 | ~2.300 |

Tokens estimados como caracteres ÷ 3,5; é uma aproximação, não a contagem exata do tokenizador. O C1 conta 39 arquivos porque inclui os `__init__.py` de cada camada.

**Estruturas resultantes:**

- **C1:** pacote `vetclinic/` com camadas separadas (`routers/`, `services/`, `repositories/`, `schemas/`) e um arquivo por recurso em cada camada.
- **C2:** um único `main.py` com tudo.
- **C3:** um módulo por recurso na raiz, cada um reunindo validação, SQL e rotas, mais `db.py` e `comum.py` compartilhados. Nas palavras do próprio modelo: um módulo por recurso, sem camadas intermediárias, nomes em português e comentários só para regras de negócio não óbvias. A lista completa de convenções que ele disse ter escrito não ficou registrada no histórico da sessão.

**Documentações:** a do C1 é um guia de onboarding em prosa (arquitetura, fluxo de uma requisição, regras e onde ficam, passo a passo para nova entidade). As do C2 e C3 são mapas densos: arquivo → símbolos, esquema do banco, cada regra de negócio com sua localização exata e convenções para código novo.

## Resultados

Todas as 120 execuções tiveram sucesso, então a comparação é inteiramente sobre custo e esforço. Valores são medianas de 5 execuções por célula.

### Custo de referência por execução (US$)

| Tarefa | C1 sem doc | C2 sem doc | C3 sem doc | C1 com doc | C2 com doc | C3 com doc |
| --- | --- | --- | --- | --- | --- | --- |
| T1 cadastro novo | 0,213 | 0,109 | 0,105 | 0,227 | 0,122 | 0,136 |
| T3 regra transversal | 0,203 | 0,104 | 0,111 | 0,230 | 0,112 | 0,119 |
| T4 bug localizado | 0,059 | 0,060 | 0,058 | 0,092 | 0,067 | 0,067 |
| T5 mudança de regra | 0,118 | 0,087 | 0,086 | 0,139 | 0,084 | 0,096 |

### Tokens de entrada (milhares)

| Tarefa | C1 sem doc | C2 sem doc | C3 sem doc | C1 com doc | C2 com doc | C3 com doc |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | 181,5 | 90,2 | 111,8 | 224,1 | 110,1 | 106,6 |
| T3 | 228,4 | 92,7 | 94,9 | 233,1 | 80,7 | 78,9 |
| T4 | 75,2 | 94,1 | 75,9 | 83,7 | 67,3 | 67,3 |
| T5 | 122,1 | 86,6 | 107,8 | 129,9 | 94,6 | 98,9 |

### Tokens de saída

| Tarefa | C1 sem doc | C2 sem doc | C3 sem doc | C1 com doc | C2 com doc | C3 com doc |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | 7.127 | 2.739 | 2.788 | 7.318 | 2.739 | 4.506 |
| T3 | 5.869 | 2.035 | 2.725 | 6.220 | 2.215 | 2.966 |
| T4 | 854 | 850 | 778 | 729 | 672 | 618 |
| T5 | 2.453 | 1.349 | 1.522 | 2.053 | 1.364 | 1.697 |

### Efeito do estilo

Sem documentação, o C1 gastou mais que C2 e C3 de forma consistente em T1, T3 e T5: o tamanho do efeito (Cliff's delta) nos tokens de saída foi +1,00 em todas essas comparações, ou seja, toda execução do C1 escreveu mais que toda execução dos outros. Nos tokens de entrada, os deltas do C1 contra C2 foram +0,76 (T1), +1,00 (T3) e +1,00 (T5). Kruskal-Wallis entre os três estilos: p = 0,032 (T1), 0,004 (T3), 0,677 (T4) e 0,002 (T5).

| Tarefa | Custo do C1 ÷ menor custo entre C2 e C3 (sem doc) |
| --- | --- |
| T1 cadastro novo | 2,0× |
| T3 regra transversal | 1,9× |
| T5 mudança de regra | 1,4× |
| T4 bug localizado | 1,0× |

C2 e C3 tiveram custo praticamente igual em todas as tarefas. A única diferença consistente foi na T5, em que o C2 usou menos tokens de entrada que o C3 (86,6 mil contra 107,8 mil), sem diferença no custo.

### Efeito da documentação

Variação do custo de referência ao adicionar a doc, por estilo:

| Tarefa | C1 (doc humana) | C2 (doc para IA) | C3 (doc para IA) |
| --- | --- | --- | --- |
| T1 | +7% | +12% | +30% |
| T3 | +13% | +8% | +7% |
| T4 | +56% | +12% | +16% |
| T5 | +18% | −3% | +12% |

A doc aumentou o custo em 11 das 12 combinações. Nos tokens de entrada o quadro é misto: as docs para IA reduziram os tokens no C3 em todas as tarefas (−5% a −17%) e no C2 em duas (T3 −13%, T4 −28%), enquanto a doc humana do C1 aumentou os tokens em todas (+2% a +23%). Mesmo onde os tokens caíram, o custo subiu.

### Comportamento do agente

| Tarefa | Condição | Bash | Grep | Read | Edit | Write |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | C1 sem doc | 28 | 0 | 0 | 0 | 0 |
| T1 | C3 sem doc | 19 | 0 | 0 | 0 | 0 |
| T1 | C3 com doc | 6 | 2 | 21 | 18 | 4 |
| T3 | C1 com doc | 22 | 0 | 0 | 0 | 0 |
| T3 | C3 com doc | 7 | 0 | 20 | 0 | 0 |
| T4 | C1 sem doc | 5 | 5 | 8 | 5 | 0 |
| T4 | C2 com doc | 5 | 5 | 0 | 5 | 0 |

Somas de 5 execuções; recorte das combinações mais ilustrativas (a tabela completa está em `resultados/analise.md`).

- **Sem doc, nas tarefas de criação, o agente trabalhou só pelo terminal:** leu arquivos e escreveu código com comandos, sem usar as ferramentas de leitura e edição.
- **A doc para IA mudou isso:** com ela, o agente passou a abrir arquivos específicos e editar trechos pontuais. No C3 na T1, isso veio com mais turnos (12 contra 5) e mais tokens de saída, o que explica o custo 30% maior.
- **A doc humana não mudou o padrão:** no C1, o agente continuou trabalhando só pelo terminal.
- **Na T4 com doc para IA, o agente foi direto à linha do bug** sem abrir nenhum arquivo inteiro.

## Por que os resultados ficaram assim

O custo do estilo humano vem de *seguir* o estilo ao escrever código, e o custo da documentação vem de ela ser paga em toda execução enquanto o projeto é pequeno demais para ela se pagar.

**Sobre o estilo**

- **Seguir convenções verbosas custa caro.** O prompt pedia para seguir as convenções do projeto. No C1, isso significou escrever em várias camadas com docstrings e type hints: 2 a 3 vezes mais tokens de saída, que são os mais caros e mais lentos de gerar.
- **Quanto mais a tarefa atravessa o sistema, maior a diferença.** A T3 mexe em tutor, atendimento e fatura ao mesmo tempo; no C1 isso envolve schema, repositório, serviço e rota de cada um, e foi onde os tokens de entrada mais se distanciaram (2,5 vezes). A T5 mexe numa regra só e teve a menor diferença (1,4 vez).
- **Tarefas localizadas não dependem do estilo.** Na T4 o agente acha a consulta SQL com uma busca textual e corrige uma linha, sem precisar entender o resto.
- **O modelo, livre, escolhe algo próximo do estilo para IA.** O C3 abandonou as camadas e reduziu comentários sem que ninguém pedisse, e ficou com o mesmo custo do C2.

**Sobre a documentação**

- **A doc entra no contexto de toda execução, útil ou não.** É por isso que o custo sobe mesmo quando o total de tokens cai: o `CLAUDE.md` é conteúdo novo no início de cada execução, cobrado como escrita de cache, que é mais cara; já a economia aparece em releituras, que são baratas. Os dados confirmam: a mediana de tokens escritos em cache subiu de 17,7 mil sem doc para 20,5 mil com doc, um acréscimo de 2,8 mil, compatível com o tamanho das docs. Sem doc, essa escrita é quase só o piso fixo de instruções e ferramentas (~17,5 mil).
- **O projeto é pequeno o bastante para explorar sem mapa.** Com o código inteiro valendo de 3 a 17 mil tokens, o agente acha o que precisa com poucos comandos; um mapa de 2 a 6 mil tokens não tem muito o que economizar.
- **A doc para IA muda a estratégia, não só o custo.** Com ela, o agente lê e edita de forma direcionada. Isso deu a execução mais previsível do estudo (T4), mas também levou a um trabalho mais metódico e caro na T1 do C3.
- **A doc humana grande foi a pior combinação.** No C1 ela somou ~5,8 mil tokens ao contexto, não mudou a forma como o agente trabalhou e não reduziu tokens em nenhuma tarefa. Na T4, que mal precisa de contexto, o custo subiu 56%.

**O que não apareceu:** nenhuma diferença de qualidade. Mesmo as tarefas mais difíceis (T3 e T5) foram resolvidas em 100% das execuções em todos os estilos, com e sem doc.

## Limitações

O efeito do estilo foi forte e consistente; o efeito da documentação é menor e mais dependente do contexto, e as condições abaixo limitam o quanto os dois se generalizam.

| Limitação | Efeito provável |
| --- | --- |
| Projeto pequeno (código de ~3 a ~17 mil tokens) | Explorar sem mapa é barato; em projetos grandes, a doc tende a valer mais e a diferença entre estilos pode crescer |
| 100% de sucesso em todas as células | Não dá para saber se algum estilo ou doc reduz erros em tarefas que o modelo erra |
| Um único modelo (Claude Sonnet 5.5) | Outros modelos podem ler estilos e docs de forma diferente |
| Mesmo modelo gerou código, doc e tarefas | Pode ter vantagem lendo o próprio estilo |
| Uma instância de cada projeto e de cada doc | Uma escolha particular pode pesar como se fosse efeito do estilo ou do tipo de doc |
| Tipo de doc amarrado ao estilo | Não separa "doc humana vs doc para IA" de "código humano vs código para IA" |
| 5 repetições por célula | Variações de 10% a 20% em algumas células são difíceis de distinguir de ruído |
| Custo de referência usa preço de API | É uma ponderação por tipo de token; o consumo real da cota da assinatura pode seguir outra proporção |
| Custo da doc conferido só no agregado | A escrita de cache subiu ~2,8 mil tokens com doc na mediana geral; não foi separada por estilo e tarefa |
| Tokens dos projetos e docs estimados (caracteres ÷ 3,5) | As tabelas de tamanho são aproximadas; os tokens das execuções são exatos |

Um ponto fica de fora por desenho: o custo para **humanos**. O C2 é o mais barato para a IA, mas ninguém mediu quanto tempo um desenvolvedor leva para revisar ou entender um arquivo único sem comentários. Para um projeto real, essa é a outra metade da decisão.

## Próximos passos

A conclusão prática até aqui: para projetos pequenos, código enxuto vale mais que documentação, e pedir ao modelo para escolher o estilo mais eficiente já basta. Os passos abaixo testariam se isso se mantém quando as condições mudam.

1. **Decompor o custo da doc:** o acréscimo de escrita de cache já foi confirmado no agregado; falta separar por estilo e tarefa, para saber quanto do custo extra vem da doc em si e quanto da mudança de comportamento do agente.
2. **Projeto maior:** repetir com um sistema de 5 a 10 vezes o tamanho, onde explorar sem mapa fica caro. É o cenário em que a documentação tem mais chance de se pagar.
3. **Tarefas que o modelo erra:** requisitos ambíguos ou mudanças em várias regras ao mesmo tempo, para sair dos 100% e medir se algum estilo leva a mais erros.
4. **Separar tipo de doc e estilo:** rodar C1 com doc para IA e C2 com doc humana, para saber se o que importa é o formato da doc ou o código.
5. **Tarefas em sequência:** aplicar várias tarefas no mesmo repositório e ver se o custo do estilo humano se acumula ao longo do tempo.
6. **Outro modelo e custo humano:** repetir as tarefas com outro modelo e medir quanto tempo desenvolvedores levam para entender cada estilo.

## Conclusão

Num projeto pequeno, código escrito para a IA deixou a criação e a alteração de funcionalidades de 27% a 49% mais baratas, sem perda de qualidade, e a documentação não se pagou. O que tornou isso seguro não foi o estilo, e sim a suíte de testes: foi ela que garantiu que os três projetos se comportavam igual e que cada tarefa estava de fato correta.

**O que o estudo mostrou:**

- O estilo do código muda o custo do agente de forma consistente, porque ele segue as convenções que encontra: código verboso gera mais código verboso.
- O efeito aparece em tarefas que criam ou alteram lógica, e some em correções localizadas.
- Não é preciso um guia de estilo detalhado: pedir ao modelo para otimizar o código para um LLM já leva a um resultado tão eficiente quanto regras explícitas.
- Documentação é um custo fixo por execução. Em projetos pequenos ela não tem o que economizar; a doc para IA muda a forma de trabalhar do agente, mas não o deixou mais barato.

### Perspectiva para a vida real

A ideia central é uma troca: quando nenhum humano precisa ler o código com frequência, a legibilidade humana deixa de ser a prioridade, e a garantia de que o sistema funciona passa a vir dos testes. A pergunta muda de "o código está legível?" para "o comportamento está garantido?".

**Onde o estilo para IA tende a compensar:**

- **Projetos pequenos feitos com vibe coding e pouca manutenção humana:** protótipos, MVPs, ferramentas internas, dashboards de uso interno. Cada nova funcionalidade sai mais barata, desde que testes de aceitação consistentes cubram o comportamento esperado.
- **Código de integração e "cola":** conectores entre sistemas, rotinas de importação e exportação, ETLs simples, scripts de automação. Se algo quebrar, o agente corrige ou reescreve contra os mesmos testes.
- **Serviços pequenos com contrato bem definido:** uma API descrita por especificação e testes de contrato. O contrato é a parte que humanos precisam entender; o interior pode ser otimizado para quem de fato o mantém, o agente.
- **Provas de conceito, spikes e hackathons:** código de vida curta, em que velocidade e custo importam mais que manutenção de longo prazo.
- **Telas administrativas e CRUDs internos:** funcionalidades repetitivas, de regra simples, que um agente estende com frequência.

**Onde o estilo humano continua sendo a escolha certa:**

- Sistemas grandes e de vida longa, mantidos e revisados por uma equipe.
- Código sujeito a auditoria ou regulação (financeiro, saúde), em que pessoas precisam conseguir ler e justificar cada regra.
- Partes críticas de segurança, em que a revisão humana é a última linha de defesa.
- Bases usadas para formar pessoas ou integrar novos desenvolvedores.

Um caminho intermediário também faz sentido: manter o núcleo de domínio, onde ficam as regras mais sensíveis, no estilo humano, e deixar a periferia (integrações, telas, scripts) no estilo para IA.

**A condição para qualquer um desses casos são testes sólidos.** Sem eles, a economia vira risco, porque ninguém está lendo o código para notar um erro. Os testes que funcionaram aqui têm três características: verificam o comportamento de fora (pela API, sem depender da estrutura interna), foram escritos e revisados por um humano antes do código, e rodam a cada mudança.

**Sobre documentação na prática:** em projetos pequenos, um `CLAUDE.md` curto com o essencial (como rodar os testes, regras não óbvias, onde fica cada coisa) tende a valer mais que um guia extenso, que é pago em toda execução. Se a documentação se paga em projetos grandes é uma pergunta que este estudo ainda não respondeu.

## Como reproduzir

Tudo o que foi usado está neste repositório; para refazer o estudo basta o Claude Code com uma conta ativa.

**Requisitos:** Linux ou macOS, Python 3.12, git e o [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) instalado e autenticado.

**Estrutura:**

| Pasta ou arquivo | Conteúdo |
| --- | --- |
| `kit/` | Molde comum: `SPEC.md`, `run.sh`, `test.sh`, `requirements.txt` e os 37 testes de aceitação |
| `projetos/C1`, `C2`, `C3` | Os três projetos gerados, na versão usada no estudo |
| `docs/` | As três documentações revisadas (`C1.md`, `C2.md`, `C3.md`) |
| `prompts/` | Prompts de geração dos projetos e das documentações |
| `tarefas/` | Prompt e testes ocultos de cada tarefa (T1, T3, T4, T5) |
| `runner.py` | Executa as tarefas e grava as métricas em `resultados/results.jsonl` |
| `analisar.py` | Gera `resultados/analise.md` e `resultados/resumo.csv` |
| `resultados/` | Métricas das 120 execuções e o log completo de cada uma |

**Passos:**

1. Crie o ambiente Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r kit/requirements.txt
```

2. Crie uma configuração limpa do Claude Code só para o estudo, para que memórias, preferências e conectores pessoais não interfiram. Faça login e desative qualquer servidor MCP listado em `/mcp`:

```bash
mkdir -p ~/.claude-estudo
CLAUDE_CONFIG_DIR=~/.claude-estudo claude
```

3. O `runner.py` exporta cada projeto a partir de uma tag git chamada `base`. Crie a tag em cada projeto:

```bash
for p in C1 C2 C3; do
  (cd projetos/$p && git init -q && git add -A && git commit -qm base && git tag base)
done
```

4. Rode as execuções e a análise. O script pula execuções já registradas e para sozinho se o limite de uso do plano for atingido; basta rodá-lo de novo depois. Para começar do zero, mova o `resultados/results.jsonl` existente para outro lugar.

```bash
python3 runner.py
python3 analisar.py
```

**Para gerar projetos e docs novos** em vez de usar os deste repositório: copie `kit/` para `projetos/Cx`, rode o Claude Code dentro da pasta com o prompt de `prompts/gerar_Cx.txt` até o `./test.sh` passar, e congele com a tag `base`. As docs saem dos prompts `prompts/doc_humana.txt` (C1) e `prompts/doc_ia.txt` (C2 e C3); revise-as contra o código antes de usar.

**Atenção:** o `runner.py` deixa o agente editar arquivos e rodar comandos sem pedir confirmação, numa cópia temporária em `/tmp`, e encerra processos `uvicorn main:app` ao fim de cada execução. Para isolamento total, rode-o dentro de um container.
