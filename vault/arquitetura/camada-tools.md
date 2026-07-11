---
tags: [arquitetura, tools]
atualizado: 2026-07-09
---

# Camada de Tools

Interface entre o [[agente-orquestrador]] e o mundo determinístico. Cada tool tem
**schema tipado (pydantic)** — entrada e saída validadas ([[guardrails]]).

## Tools

### `calcular_metricas`
Executa SQL determinístico sobre o Postgres ([[camada-dados]]) e devolve as 4 [[metricas]].
Sem interpretação — só números + metadados (período, N).

### `dados_grafico`
Devolve as séries temporais dos 2 gráficos (30 dias / 12 meses). Renderização fica na
[[geracao-relatorio]].

### `buscar_noticias`
Consulta a **NewsAPI** ([[adr-0002-fonte-noticias]]) por notícias de SRAG em tempo real.
Aplica filtro de relevância antes de devolver ([[guardrails]]).

## Princípios

- Tools **não alucinam**: retornam dados de fonte, ou erro explícito.
- Toda chamada é registrada com entrada/saída ([[governanca-auditoria]]).
- Funções de métrica são **puras e testáveis** (pytest — ver [[stack]]).
