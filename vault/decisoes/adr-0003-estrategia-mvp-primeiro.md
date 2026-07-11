---
tags: [decisao, adr, processo]
status: aceito
data: 2026-07-09
---

# ADR-0003 — Estratégia: MVP antes da PoC completa

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
A meta é uma PoC completa, mas o desafio orienta "entregue o que conseguir".
Risco de gastar tempo em refinamento antes de ter algo funcional.

## Decisão
Construir primeiro um **MVP ponta-a-ponta** (grafo linear, guardrails mínimos) e só
então endurecer até a PoC completa. Ver [[fases]].

## Alternativas consideradas
- Ir direto para a PoC completa — maior risco de não fechar o ciclo a tempo.

## Consequências
- Sempre há um artefato entregável ao fim de cada iteração.
- Governança/guardrails robustos entram na fase de endurecimento, não no MVP.

## Relacionadas
[[fases]] · [[visao-geral]]
