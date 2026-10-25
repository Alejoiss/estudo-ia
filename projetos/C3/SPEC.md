# VetClinic API — Especificação

API REST de gestão de uma clínica veterinária. Este documento é o contrato: rotas, campos,
códigos de status e regras de negócio são obrigatórios e verificados pela suíte de aceitação
em `tests/acceptance`.

## Restrições técnicas

- Python 3.12, FastAPI, banco SQLite usando o módulo `sqlite3` da biblioteca padrão (sem ORM).
- Apenas as dependências de `requirements.txt`.
- O arquivo `main.py` na raiz do projeto deve expor o objeto FastAPI como `app`
  (o `run.sh` executa `uvicorn main:app`). A organização do restante do código é livre.
- Caminho do banco: variável de ambiente `DB_PATH` (padrão: `vetclinic.db`). As tabelas são
  criadas na inicialização, se não existirem.
- `run.sh`, `test.sh`, `requirements.txt`, `SPEC.md` e `tests/acceptance/` não podem ser alterados.

## Convenções gerais

- Corpo das requisições e respostas em JSON.
- Datas: `"YYYY-MM-DD"`. Data e hora: `"YYYY-MM-DDTHH:MM"` (hora local, sem fuso, sem segundos).
- Valores monetários sempre em centavos, como inteiros (`*_centavos`). Valor não inteiro → 422.
- IDs são inteiros gerados pelo sistema.
- Listagens retornam uma lista JSON, ordenada por `id` crescente, salvo indicação contrária.
- Erros:
  - `404` recurso inexistente (inclusive IDs referenciados no corpo, como `tutor_id`).
  - `409` conflito com o estado atual (regra de negócio violada pelo estado).
  - `422` dados inválidos (formato, campo obrigatório ausente, valor fora da faixa, regra de validação).
  - Corpo do erro: `{"detail": "<mensagem>"}` (a mensagem é livre; a validação automática do
    FastAPI também é aceita para 422).
- Strings obrigatórias não podem ser vazias nem conter só espaços (→ 422).

## Recursos

### Tutores

Campos: `id`, `nome` (obrigatório), `email` (obrigatório, deve conter `@`), `telefone` (opcional, string ou `null`).

| Método | Rota | Sucesso | Observações |
| --- | --- | --- | --- |
| POST | `/tutores` | 201, tutor | |
| GET | `/tutores` | 200, lista | |
| GET | `/tutores/{id}` | 200, tutor | 404 |
| PUT | `/tutores/{id}` | 200, tutor | mesmo corpo do POST; 404 |
| DELETE | `/tutores/{id}` | 204, sem corpo | 404; **409 se o tutor tiver pets** |
| GET | `/tutores/{id}/pets` | 200, lista de pets | 404 |
| GET | `/tutores/{id}/faturas` | 200, lista de faturas | 404 |

### Pets

Campos: `id`, `nome` (obrigatório), `especie` (`"cao"`, `"gato"` ou `"outro"`),
`tutor_id` (obrigatório), `data_nascimento` (opcional, data ou `null`; não pode ser futura → 422).

| Método | Rota | Sucesso | Observações |
| --- | --- | --- | --- |
| POST | `/pets` | 201, pet | 404 se `tutor_id` não existe |
| GET | `/pets/{id}` | 200, pet | 404 |
| PUT | `/pets/{id}` | 200, pet | mesmo corpo do POST; 404 |
| DELETE | `/pets/{id}` | 204 | 404; **409 se o pet tiver agendamentos** |

### Veterinários

Campos: `id`, `nome` (obrigatório), `crmv` (obrigatório, único).

| Método | Rota | Sucesso | Observações |
| --- | --- | --- | --- |
| POST | `/veterinarios` | 201, veterinário | **409 se o `crmv` já existir** |
| GET | `/veterinarios` | 200, lista | |
| GET | `/veterinarios/{id}` | 200, veterinário | 404 |

### Produtos

Campos: `id`, `nome` (obrigatório), `preco_centavos` (inteiro ≥ 0), `estoque` (inteiro ≥ 0),
`estoque_minimo` (inteiro ≥ 0).

| Método | Rota | Sucesso | Observações |
| --- | --- | --- | --- |
| POST | `/produtos` | 201, produto | |
| GET | `/produtos` | 200, lista | |
| GET | `/produtos/{id}` | 200, produto | 404 |
| POST | `/produtos/{id}/entrada` | 200, produto atualizado | corpo `{"quantidade": int > 0}`; soma ao estoque; 404 |

### Agendamentos

Campos de resposta: `id`, `pet_id`, `veterinario_id`, `inicio`, `fim`, `duracao_minutos`, `status`.

Entrada do POST: `pet_id`, `veterinario_id`, `inicio`, `duracao_minutos` (opcional, padrão 30).

`status`: `"agendado"`, `"concluido"`, `"cancelado"` ou `"cancelado_tardio"`.

| Método | Rota | Sucesso | Observações |
| --- | --- | --- | --- |
| POST | `/agendamentos` | 201, agendamento (`status` = `"agendado"`) | regras abaixo |
| GET | `/agendamentos/{id}` | 200, agendamento | 404 |
| GET | `/agendamentos?veterinario_id=X&data=YYYY-MM-DD` | 200, lista ordenada por `inicio` | ambos os filtros opcionais e combináveis |
| POST | `/agendamentos/{id}/cancelar` | 200, agendamento | regras abaixo |

**Regras de criação** (verificadas nesta ordem; a primeira que falhar define a resposta):

1. `pet_id` ou `veterinario_id` inexistente → 404.
2. `duracao_minutos` deve ser múltiplo de 15, entre 15 e 120 → senão 422.
3. `inicio` deve ser posterior ao momento atual → senão 422.
4. Expediente: o intervalo inteiro `[inicio, fim]` deve estar dentro do horário de funcionamento,
   no mesmo dia → senão 422.
   - Segunda a sexta: 08:00 às 18:00.
   - Sábado: 08:00 às 12:00.
   - Domingo: fechado.
   - Exemplo: consulta de 30 min às 17:30 numa terça é válida (termina 18:00); às 17:45 não é.
5. Conflito de agenda: o veterinário não pode ter outro agendamento com `status` `"agendado"` ou
   `"concluido"` que se sobreponha ao novo → senão 409.
   Intervalos são semiabertos `[inicio, fim)`: uma consulta que termina às 10:30 **não** conflita
   com outra que começa às 10:30. Agendamentos cancelados liberam o horário.

`fim` = `inicio` + `duracao_minutos`.

**Regras de cancelamento:**

- Corpo opcional: `{"momento": "YYYY-MM-DDTHH:MM"}`. Indica o instante do cancelamento;
  se ausente, usa o momento atual (o campo existe para permitir testes determinísticos).
- Só agendamentos com `status` `"agendado"` podem ser cancelados → senão 409. 404 se não existir.
- Se faltarem **24 horas ou mais** entre `momento` e `inicio`: `status` = `"cancelado"`.
- Se faltarem menos de 24 horas: `status` = `"cancelado_tardio"`.

### Atendimentos

Um atendimento registra a consulta realizada e gera a fatura.

Entrada: `anotacoes` (string, pode ser vazia), `produtos` (lista, pode ser vazia) de
`{"produto_id": int, "quantidade": int > 0}`.

Resposta: `id`, `agendamento_id`, `anotacoes`, `produtos` (como enviados), `fatura_id`.

| Método | Rota | Sucesso | Observações |
| --- | --- | --- | --- |
| POST | `/agendamentos/{id}/atendimento` | 201, atendimento | regras abaixo |
| GET | `/atendimentos/{id}` | 200, atendimento | 404 |

**Regras:**

1. Agendamento inexistente → 404. Produto inexistente → 404.
2. Só agendamentos com `status` `"agendado"` → senão 409.
3. Estoque insuficiente para qualquer produto → 409, e **nada** é alterado (nem estoque, nem
   agendamento, nem fatura).
4. Em caso de sucesso, na mesma transação:
   - o agendamento passa para `"concluido"`;
   - o estoque de cada produto é reduzido pela quantidade usada;
   - é criada uma fatura `"aberta"` para o tutor do pet, com os itens descritos abaixo.

### Faturas

Campos: `id`, `tutor_id`, `atendimento_id` (ou `null`), `status` (`"aberta"` ou `"paga"`),
`itens`, `total_centavos`.

Cada item: `descricao`, `quantidade`, `valor_unitario_centavos`, `total_centavos`
(= `quantidade` × `valor_unitario_centavos`).

Fatura de atendimento, itens nesta ordem:
1. `{"descricao": "Consulta", "quantidade": 1, "valor_unitario_centavos": 15000, ...}`
   (valor fixo da consulta: 15000 centavos).
2. Um item por produto usado, na ordem enviada: `descricao` = nome do produto,
   `valor_unitario_centavos` = preço do produto no momento do atendimento.

`total_centavos` da fatura = soma dos `total_centavos` dos itens.

| Método | Rota | Sucesso | Observações |
| --- | --- | --- | --- |
| GET | `/faturas/{id}` | 200, fatura | 404 |
| POST | `/faturas/{id}/itens` | 200, fatura atualizada | corpo `{"descricao", "quantidade" > 0, "valor_unitario_centavos" ≥ 0}`; 404; **409 se paga** |
| POST | `/faturas/{id}/pagar` | 200, fatura com `status` `"paga"` | 404; **409 se já paga** |
