---
tags: [decisao, adr, observabilidade]
status: aceito
data: 2026-07-09
---

# ADR-0012 — Observabilidade: structlog + OpenTelemetry + trilha de auditoria

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
O critério de **Governança/Transparência** exige registro das decisões dos agentes.
Precisamos correlacionar logs, traces e a trilha de auditoria de cada execução.

## Decisão
Adotar **structlog** (logs JSON), **OpenTelemetry** (spans por nó/adapter) e uma
**trilha de auditoria** persistida por execução, todos correlacionados por um `run_id`.
Detalhes em [[qualidade-governanca]].

## Alternativas consideradas
- `print`/logging básico — insuficiente para auditoria estruturada.
- Só LangSmith — útil, mas cria dependência externa; a trilha própria é soberana.

## Consequências
- Cada execução é totalmente rastreável ([[qualidade-governanca]]).
- Overhead de instrumentação, isolado da lógica de domínio ([[arquitetura]]).
- Dados sensíveis nunca são logados ([[qualidade-governanca]]).

## Relacionadas
[[qualidade-governanca]] · [[qualidade-governanca]] · [[qualidade-governanca]]
