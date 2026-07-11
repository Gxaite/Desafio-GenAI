---
tags: [arquitetura, governanca]
atualizado: 2026-07-09
---

# Governança e Auditoria

Atende diretamente o critério **"Governança e Transparência — registro de decisões
dos agentes"** ([[criterios-avaliacao]]). É transversal a toda a [[visao-geral]].

## Trilha de auditoria

Cada execução gera uma trilha estruturada (JSON), registrando por evento:

- `timestamp`, `no` (nó do grafo), `tipo` (decisão / tool_call / llm)
- entrada, saída (ou resumo), modelo usado, duração
- erros e fallbacks

O grafo do [[agente-orquestrador]] favorece isso: cada nó = um ponto de log.

## Transparência no output

- Relatório traz rodapé com **modelo, fontes de notícias e timestamp** ([[geracao-relatorio]]).
- Premissas metodológicas explícitas ([[adr-0007-metricas-proxy]]).
- Contagens de limpeza do ETL registradas ([[camada-dados]]).

## Relação com o vault

Este vault **é parte da governança**: as [[template-adr|ADRs]] documentam *por que*
cada decisão foi tomada, não só *o que* foi feito.
