---
tags: [planejamento]
atualizado: 2026-07-09
---

# Fases de Implementação

Estratégia: **MVP ponta-a-ponta primeiro, depois endurecer até PoC completa**
([[adr-0003-estrategia-mvp-primeiro]]).

## Fase 0 — Dados ✅
Sondagem dos CSVs reais (encoding, colunas, domínios, dedup) — achados em [[srag-datasus]]
e [[camada-dados]].

## Fase 1 — ETL medallion ✅
EL (Python → bronze) + dbt (silver limpo/dedup → gold agregado) no Postgres, com `dbt test`
em cada camada ([[camada-dados]], [[adr-0015-dbt-medallion]]). Infra Docker (compose/Postgres/
Grafana) sobe junto — ver [[arquitetura]]. **Verificado:** 491.106 casos → mart gold com
14.906 linhas, 14/14 testes PASS.

## Fase 2 — Tools de métricas e gráficos ⬜ (próxima)
Funções puras, determinísticas e testáveis sobre o mart gold ([[camada-tools]], [[metricas]]).

## Fase 3 — Tool de notícias
Integração com NewsAPI ([[adr-0002-fonte-noticias]]).

## Fase 4 — Agente + governança + guardrails
Grafo [[agente-orquestrador]] (LangGraph) + governança/auditoria e guardrails ([[qualidade-governanca]]).

## Fase 5 — Relatório e documentação
[[geracao-relatorio]] (PDF), README e diagrama de arquitetura.

---

## Corte do MVP (Fases 1→5, versão mínima)
Grafo **linear**: `calcular métricas → buscar notícias → narrar → montar relatório`.
Sem loops/condicionais, guardrails mínimos. Meta: sair um PDF com os 4 números +
2 gráficos + 1 parágrafo de contexto. Depois iteramos.
