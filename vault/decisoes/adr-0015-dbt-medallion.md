---
tags: [decisao, adr, dados]
status: aceito
data: 2026-07-11
---

# ADR-0015 — Transformação com dbt em arquitetura medallion

- **Status:** aceito
- **Data:** 2026-07-11

## Contexto
Precisamos transformar o CSV bruto de SRAG (554 MB, 194 colunas) nos marts que alimentam
métricas, gráficos e Grafana. Cogitou-se DuckDB e depois pandas como motor de agregação
([[adr-0006-duckdb]]). Sendo o Postgres o store servido e o avaliador uma casa de dados,
buscou-se uma transformação **versionada, testável e com lineage**.

## Decisão
Transformação em **dbt** (adapter Postgres) sobre uma **arquitetura medallion**:

- **EL (Python, `srag_etl`)** — lê os CSVs e faz `COPY` de **apenas as ~6 colunas
  necessárias** (minimização LGPD) para `bronze.srag_raw`. Só carrega; não transforma.
- **🥉 bronze** — landing bruto (texto), 1 linha por registro + arquivo de origem.
- **🥈 silver** (`silver.srag_casos`) — dbt: limpo, tipado e **deduplicado** por
  `NU_NOTIFIC`; 1 linha por caso.
- **🥇 gold** (`gold.mart_srag_diario`) — dbt: **agregado** por (dia, UF). Único artefato
  servido ao `backend` e ao `grafana`.
- **`dbt test`** em cada camada: `not_null`, `unique`, `accepted_values`, grão único.

## Alternativas consideradas
- **pandas em memória** — simples e mantém o bruto fora do Postgres, mas sem testes de
  dados, lineage nem documentação versionada.
- **DuckDB** — motor rápido de CSV, porém +1 tecnologia e mesma lacuna de governança de dados.
- **ELT SQL puro (sem dbt)** — perde os `tests`/docs/lineage que justificam a escolha.

## Consequências
- **+dbt-postgres** na stack e um passo EL antes do dbt.
- **Trade-off LGPD:** o bruto (minimizado a ~6 colunas) transita pelo Postgres nas camadas
  bronze/silver. Mitigação: só as colunas necessárias entram; **apenas a gold é servida**;
  bronze/silver são internas. Ver [[qualidade-governanca]].
- Ganho de governança de dados: modelos SQL versionados, testes automatizados e lineage —
  reforça *Clean Code* e transparência.

## Relacionadas
[[camada-dados]] · [[adr-0006-duckdb]] · [[qualidade-governanca]] · [[arquitetura]]
