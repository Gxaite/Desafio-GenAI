---
tags: [decisao, adr, noticias]
status: aceito
data: 2026-07-09
---

# ADR-0002 — Fonte de Notícias: NewsAPI

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
O agente precisa consultar notícias de SRAG **em tempo real** para embasar as métricas.

## Decisão
Usar a **NewsAPI** como fonte, encapsulada na tool `buscar_noticias` ([[camada-tools]]).

## Alternativas consideradas
- Google News RSS — grátis e sem chave, mas menos estruturado.
- Tavily — boa integração com agentes, mas optamos por NewsAPI.

## Consequências
- Requer chave de API no `.env` ([[dados-sensiveis]]).
- Resultados estruturados facilitam o filtro de relevância ([[guardrails]]).
- Atenção a limites do tier gratuito.

## Relacionadas
[[camada-tools]] · [[guardrails]]
