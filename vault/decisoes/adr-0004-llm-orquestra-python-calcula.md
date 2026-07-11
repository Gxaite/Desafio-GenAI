---
tags: [decisao, adr, principio]
status: aceito
data: 2026-07-09
---

# ADR-0004 — Princípio: o LLM orquestra e explica; o Python calcula

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
LLMs erram em aritmética e podem alucinar números. As [[metricas]] precisam ser
corretas e auditáveis.

## Decisão
Todas as métricas são calculadas por **SQL/Python determinístico**. O LLM **nunca**
calcula: ele apenas orquestra as tools e escreve a narrativa a partir dos números
retornados.

## Alternativas consideradas
- Deixar o agente calcular via "code interpreter"/raciocínio — descartado por risco de
  correção e auditabilidade.

## Consequências
- Métricas viram funções puras testáveis ([[camada-tools]], [[stack]]).
- Base para o guardrail de *grounding* ([[guardrails]]).
- Facilita a trilha de auditoria ([[governanca-auditoria]]).

## Relacionadas
[[camada-tools]] · [[guardrails]] · [[metricas]]
