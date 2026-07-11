---
tags: [arquitetura, moc]
atualizado: 2026-07-09
---

# Arquitetura — Visão Geral

Solução em 4 camadas, com auditoria e guardrails transversais. Guiada pelo princípio
[[adr-0004-llm-orquestra-python-calcula]]: **o LLM orquestra e explica; o Python calcula**.

```
┌─────────────────────────────────────────────────────────┐
│  1. CAMADA DE DADOS  → [[camada-dados]]                  │
│     CSV DATASUS → limpeza → marts no Postgres            │
├─────────────────────────────────────────────────────────┤
│  2. CAMADA DE TOOLS  → [[camada-tools]]                  │
│     calcular_metricas · dados_grafico · buscar_noticias  │
├─────────────────────────────────────────────────────────┤
│  3. AGENTE ORQUESTRADOR → [[agente-orquestrador]]        │
│     grafo LangGraph, cada nó logado                      │
├─────────────────────────────────────────────────────────┤
│  4. GERAÇÃO DE RELATÓRIO → [[geracao-relatorio]]         │
│     métricas + 2 gráficos + narrativa → PDF              │
├─────────────────────────────────────────────────────────┤
│  ⟳ TRANSVERSAL: [[governanca-auditoria]] + [[guardrails]]│
└─────────────────────────────────────────────────────────┘
```

## Fluxo do agente (MVP linear)

`calcular_metricas` → `dados_grafico` → `buscar_noticias` → `narrar (LLM)` → `montar relatório`

Na versão PoC completa o grafo ganha condicionais (ex.: re-consulta se dado ausente)
e validações entre nós — ver [[agente-orquestrador]] e [[guardrails]].

## Diagrama conceitual (entregável)
O PDF exigido pelo desafio deriva desta nota: Orquestrador + Tools + LLM + Banco +
Fontes de notícias. Ver [[criterios-avaliacao]].

## Fundamentos de engenharia
Esta visão assenta sobre [[principios]] (hexagonal/SOLID) e materializa-se em
[[estrutura-projeto]], com [[resiliencia]], [[observabilidade]], [[tratamento-erros]]
e [[qualidade-tooling]] como pilares transversais. Roda em **Docker** ([[containerizacao]])
com dashboards no **Grafana** ([[visualizacao-bi]]).

## Decisões que sustentam esta arquitetura
[[adr-0008-arquitetura-hexagonal]] · [[adr-0004-llm-orquestra-python-calcula]] ·
[[adr-0005-langgraph]] · [[adr-0006-duckdb]] · [[adr-0001-provedor-llm]] ·
[[adr-0002-fonte-noticias]] · [[adr-0010-resiliencia]] · [[adr-0012-observabilidade]] ·
[[adr-0009-tooling-uv-ruff-mypy]] · [[adr-0011-async-io]]
