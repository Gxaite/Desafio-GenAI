---
tags: [planejamento]
atualizado: 2026-07-09
---

# Fases de Implementação

Estratégia: **MVP ponta-a-ponta primeiro, depois endurecer até PoC completa**
([[adr-0003-estrategia-mvp-primeiro]]).

## Fase 0 — Dados
Baixar o CSV do Open DATASUS, explorar e mapear as ~100 colunas contra as [[metricas]].
Ver [[srag-datasus]].

## Fase 1 — ETL
Limpeza + dedup (2025+2026) + seleção de colunas; transformação com DuckDB/pandas em
memória e **carga dos marts agregados no Postgres** ([[camada-dados]]).
Já resolve boa parte de [[dados-sensiveis]]. Infra (Docker/compose/Postgres/Grafana) sobe
junto — ver [[containerizacao]].

## Fase 2 — Tools de métricas e gráficos
Funções puras, determinísticas e testáveis ([[camada-tools]]).

## Fase 3 — Tool de notícias
Integração com NewsAPI ([[adr-0002-fonte-noticias]]).

## Fase 4 — Agente + governança + guardrails
Grafo [[agente-orquestrador]] (LangGraph), [[governanca-auditoria]], [[guardrails]].

## Fase 5 — Relatório e documentação
[[geracao-relatorio]] (PDF), README e diagrama de arquitetura.

---

## Corte do MVP (Fases 1→5, versão mínima)
Grafo **linear**: `calcular métricas → buscar notícias → narrar → montar relatório`.
Sem loops/condicionais, guardrails mínimos. Meta: sair um PDF com os 4 números +
2 gráficos + 1 parágrafo de contexto. Depois iteramos.
