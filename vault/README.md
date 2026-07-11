# Vault — Desafio GenAI (SRAG / DATASUS)

Documentação de projeto: arquitetura, domínio e decisões. Mantém o *porquê* de cada escolha —
serve de trilha de auditoria e alimenta o README do repositório. Requisitos do desafio em
[`../requisitos.md`](../requisitos.md).

## Design
- [[arquitetura]] — visão em 4 camadas, princípios (hexagonal/SOLID/12-factor), estrutura de
  projeto, containerização e stack.
- [[qualidade-governanca]] — governança/auditoria, guardrails, dados sensíveis (LGPD),
  observabilidade, resiliência, erros e tooling.

## Camadas
- [[camada-dados]] — ETL do CSV DATASUS → marts no Postgres.
- [[camada-tools]] — as 3 tools do agente (`calcular_metricas`, `dados_grafico`, `buscar_noticias`).
- [[agente-orquestrador]] — grafo LangGraph.
- [[geracao-relatorio]] — métricas + 2 gráficos + narrativa → PDF.

## Domínio
- [[metricas]] — as 4 métricas + 2 gráficos exigidos.
- [[srag-datasus]] — sobre a base de dados.

## Decisões
- [[roadmap]] — plano de implementação (MVP → PoC completa).
- `decisoes/` — ADRs 0001–0015 (uma nota por decisão, com contexto e alternativas).
