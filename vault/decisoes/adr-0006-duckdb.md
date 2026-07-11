---
tags: [decisao, adr, dados]
status: aceito
data: 2026-07-09
revisa: versão anterior elegia DuckDB como store
---

# ADR-0006 — Store analítico: Postgres (DuckDB como motor de transformação)

- **Status:** aceito (**revisa** a decisão anterior, que elegia DuckDB como store)
- **Data:** 2026-07-09

## Contexto
A versão original elegeu DuckDB (embarcado) como store. Com a virada para **arquitetura
Docker multi-serviço** ([[adr-0013-containerizacao]]) — `backend`, job de `dados` e
**Grafana** ([[adr-0014-grafana]]) acessando os mesmos dados — um arquivo DuckDB
compartilhado por volume fica frágil: **single-writer**, travas de arquivo e drivers de
BI imaturos.

## Decisão
- **Postgres** como **store analítico servido** — lido por `backend` e `grafana`.
- **DuckDB + pandas** permanecem como **motor de transformação em memória** dentro do
  ETL (`dados`): limpam o CSV pesado (194 colunas) e **carregam os marts no Postgres**.

## Alternativas consideradas
- DuckDB compartilhado por volume — frágil em multi-container (locks, single-writer).
- Só pandas em memória — sem SQL servido nem acesso concorrente.
- SQLite — mesmos limites de banco embarcado.

## Consequências
- +1 container (`postgres`), porém **datasource nativo** para o Grafana e acesso
  concorrente seguro.
- Modelagem **relacional** dos marts (fato + dimensões/agregados).
- DuckDB segue útil pela velocidade de transformação sobre CSV.

## Relacionadas
[[camada-dados]] · [[adr-0013-containerizacao]] · [[adr-0014-grafana]] · [[visualizacao-bi]] · [[stack]]
