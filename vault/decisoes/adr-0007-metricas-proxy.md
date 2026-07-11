---
tags: [decisao, adr, metricas, metodologia]
status: aceito
data: 2026-07-09
---

# ADR-0007 — Ocupação de UTI e Vacinação são proxies

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
Os microdados do [[srag-datasus]] trazem **status por caso**, não cobertura populacional
nem leitos totais. Duas métricas exigidas não têm definição literal na base.

## Decisão
Adotar *proxies* explícitos e **documentá-los no relatório**:
- **Ocupação de UTI** → proporção de internados com `UTI == 1` (não "leitos ocupados/total").
- **Vacinação** → % de **casos** vacinados (`VACINA_COV`), não cobertura da população.

## Alternativas consideradas
- Cruzar com dados externos (leitos CNES, cobertura vacinal IBGE/PNI) — fora do escopo da PoC.
- Omitir as métricas — descartado; o desafio as exige.

## Consequências
- Premissas viram nota metodológica no relatório ([[geracao-relatorio]]) — rigor premiado
  em critérios de avaliação.
- Deixa aberta a evolução futura (enriquecer com dados populacionais).

## Relacionadas
[[metricas]] · [[geracao-relatorio]] · [[qualidade-governanca]]
