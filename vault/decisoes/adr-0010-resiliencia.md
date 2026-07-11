---
tags: [decisao, adr, resiliencia]
status: aceito
data: 2026-07-09
---

# ADR-0010 — Estratégia de Resiliência

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
O agente depende de serviços externos falíveis (NewsAPI, LLM/OpenRouter). O sistema
precisa ser **resiliente** e degradar com elegância.

## Decisão
Aplicar, nos adapters de infraestrutura: **timeouts** explícitos, **retry com backoff
exponencial + jitter** (`tenacity`) para erros transitórios, **circuit breaker**,
**degradação graciosa** (relatório sai sem notícias) e **fallback de modelo LLM**.
Detalhes em [[qualidade-governanca]].

## Alternativas consideradas
- "Happy path" apenas — frágil, reprovaria no critério de robustez.
- Retry infinito sem breaker — risco de martelar serviço caído.

## Consequências
- Complexidade concentrada na infraestrutura; domínio permanece puro ([[arquitetura]]).
- Toda falha/fallback é auditada ([[qualidade-governanca]]).

## Relacionadas
[[qualidade-governanca]] · [[qualidade-governanca]] · [[adr-0001-provedor-llm]]
