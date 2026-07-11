---
tags: [decisao, adr, dados]
status: aceito
data: 2026-07-09
revisa: versão anterior elegia DuckDB como store
---

# ADR-0006 — Store analítico: Postgres

- **Status:** aceito (**revisa** a decisão anterior, que elegia DuckDB como store)
- **Data:** 2026-07-09 (atualizado em 2026-07-11)

## Contexto
A versão original elegeu DuckDB (embarcado) como store. Com a virada para **arquitetura
Docker multi-serviço** ([[adr-0013-containerizacao]]) — `backend`, job de `dados` e
**Grafana** ([[adr-0014-grafana]]) acessando os mesmos dados — um arquivo DuckDB
compartilhado por volume fica frágil: **single-writer**, travas de arquivo e drivers de
BI imaturos.

## Decisão
- **Postgres** como **store analítico servido** — lido por `backend` e `grafana`.
- O **motor de transformação** deixou de ser DuckDB/pandas: a transformação passou a ser
  **EL (Python) + dbt** numa arquitetura medallion — ver [[adr-0015-dbt-medallion]].

## Alternativas consideradas
- DuckDB compartilhado por volume — frágil em multi-container (locks, single-writer).
- Só pandas em memória — sem SQL servido nem acesso concorrente.
- SQLite — mesmos limites de banco embarcado.

## Consequências
- +1 container (`postgres`), porém **datasource nativo** para o Grafana e acesso
  concorrente seguro.
- Modelagem **relacional** dos marts (camada gold agregada).

## Relacionadas
[[camada-dados]] · [[adr-0015-dbt-medallion]] · [[adr-0013-containerizacao]] · [[adr-0014-grafana]] · [[arquitetura]]
