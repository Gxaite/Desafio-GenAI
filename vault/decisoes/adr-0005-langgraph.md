---
tags: [decisao, adr, arquitetura]
status: aceito
data: 2026-07-09
---

# ADR-0005 — Framework de Orquestração: LangGraph

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
O critério de **Governança/Transparência** exige registro das decisões dos agentes.
Precisamos de um fluxo auditável, não uma caixa-preta.

## Decisão
Orquestrar com **LangGraph**: grafo de estados explícito, onde cada nó é um ponto de
decisão logável. Ver [[agente-orquestrador]].

## Alternativas consideradas
- Agente ReAct simples (LangChain) — mais rápido de montar, mas difícil de auditar.
- Orquestração 100% custom — reinventa a roda.

## Consequências
- Cada transição do grafo é registrada na trilha ([[governanca-auditoria]]).
- Habilita arestas condicionais para a fase PoC (re-consulta, validações).
- Curva de aprendizado maior que um agente linear — aceitável pelo ganho em auditoria.

## Relacionadas
[[agente-orquestrador]] · [[governanca-auditoria]] · [[adr-0001-provedor-llm]]
