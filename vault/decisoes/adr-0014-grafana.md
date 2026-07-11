---
tags: [decisao, adr, visualizacao, observabilidade]
status: aceito
data: 2026-07-09
revisa: substitui a cogitação de Metabase
---

# ADR-0014 — Grafana como camada de dashboard

- **Status:** aceito (**substitui** a cogitação anterior de Metabase)
- **Data:** 2026-07-09

## Contexto
Além dos 2 gráficos obrigatórios embutidos no relatório PDF, uma camada interativa de
visualização agrega valor. Grafana também é a ferramenta citada no contexto da vaga.

## Decisão
Usar **Grafana** como camada de dashboard/observabilidade, lendo o **Postgres**
(datasource nativo). Dashboards e datasources **provisionados como código** (YAML/JSON
versionados). Detalhes em [[visualizacao-bi]].

## Alternativas consideradas
- Metabase — bom, mas menos alinhado ao contexto e datasource de séries temporais menos forte.
- Superset — stack pesada (Postgres/Redis próprios).
- Frontend React/TS dedicado — **fora de escopo** (não é requisito do desafio; ver memória de foco).

## Consequências
- Séries temporais (casos diários/mensais) muito bem servidas.
- Provisioning-as-code reforça reprodutibilidade ([[adr-0013-containerizacao]]) e governança ([[governanca-auditoria]]).
- **Bônus, não núcleo**: o entregável obrigatório continua sendo o relatório PDF ([[geracao-relatorio]]); Grafana é cortável se o tempo apertar.

## Relacionadas
[[visualizacao-bi]] · [[adr-0006-duckdb]] · [[observabilidade]] · [[geracao-relatorio]]
