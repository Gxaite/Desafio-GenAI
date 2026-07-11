---
tags: [arquitetura, observabilidade]
atualizado: 2026-07-09
---

# Observabilidade

Três pilares, implementados em `src/srag_report/observability/` ([[estrutura-projeto]]).
Complementa e alimenta a [[governanca-auditoria]]. Decisão em [[adr-0012-observabilidade]].

## 1. Logs estruturados
`structlog` emitindo **JSON**, com `run_id` (correlation id) em todo evento. Nada de `print`.

## 2. Tracing
Spans (OpenTelemetry) por nó do grafo ([[agente-orquestrador]]) e por chamada de adapter,
medindo latência e propagando o `run_id`. Exportável para console/OTLP.

## 3. Trilha de auditoria
Registro de **decisões do agente** e **tool calls** (entrada, saída, modelo, duração),
persistido por execução → é o artefato central de [[governanca-auditoria]].

## Princípios
- **Um `run_id` correlaciona** log, trace e trilha de auditoria da mesma execução.
- Observabilidade é transversal, mas **não polui o domínio**: injetada via ports/decorators.
- Dados sensíveis **nunca** entram em logs ([[dados-sensiveis]]).

## Ligações
[[governanca-auditoria]] · [[resiliencia]] · [[guardrails]]
