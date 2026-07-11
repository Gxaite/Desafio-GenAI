---
tags: [decisao, adr, dados]
status: aceito
data: 2026-07-11
---

# ADR-0016 — Modelagem dimensional (star schema) na camada gold

- **Status:** aceito
- **Data:** 2026-07-11

## Contexto
A gold servia um único mart agregado. Sendo um projeto de **engenharia de dados**, buscou-se
uma modelagem de referência: layering idiomático dbt e um modelo dimensional explícito,
mantendo a estabilidade do contrato consumido pelo backend/Grafana.

## Decisão
Adotar **star schema** na gold, sobre o layering dbt **staging → intermediate → marts**
(mapeado ao medallion — [[adr-0015-dbt-medallion]]):

- **staging** (`stg_srag__casos`, view): tipagem/renome 1:1 da fonte bronze.
- **intermediate** (`int_srag__casos`, table): dedup por notificação + flags de negócio.
- **marts / dimensões**: `dim_uf` (via **seed** versionado → nome/região) e `dim_data` (calendário).
- **marts / fato**: `fct_srag_diario`, grão (dia, UF), medidas aditivas, FKs para as dimensões.
- **view de serviço** `gold_mart_srag_diario`: denormaliza o fato com `dim_uf`, mantendo os
  nomes de coluna esperados pela camada de tools (contrato estável — backend/Grafana não mudam).

Qualidade imposta por `dbt test`: `relationships` (fato → dims), grão único, coerência de
medidas, `accepted_values`, `not_null`, `unique`. **Lineage** via `exposures` (relatório + Grafana).

## Alternativas consideradas
- **Mart único desnormalizado** (versão anterior) — simples, mas sem dimensões reutilizáveis,
  sem lineage explícito e sem separação staging/intermediate.
- **One Big Table** — fácil de consultar, mas mistura grão e dificulta governança/testes.

## Consequências
- Dimensões reutilizáveis (`dim_uf`/`dim_data`) habilitam recortes (região, calendário) no
  Grafana sem tocar no fato.
- Mais objetos e testes (34 no `dbt build`), porém contrato de serviço inalterado.
- Star schema minimizado a `dim_uf` + `dim_data` por LGPD (sem dimensões demográficas de
  indivíduo) — ver [[qualidade-governanca]].

## Relacionadas
[[camada-dados]] · [[adr-0015-dbt-medallion]] · [[adr-0006-duckdb]] · [[metricas]]
