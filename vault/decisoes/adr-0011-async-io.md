---
tags: [decisao, adr, arquitetura]
status: aceito
data: 2026-07-09
---

# ADR-0011 — I/O assíncrono nos adapters, domínio síncrono

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
Chamadas a NewsAPI e LLM são I/O-bound; LangGraph suporta execução assíncrona. Mas
assincronismo excessivo complica o núcleo.

## Decisão
Adapters de I/O (notícias, LLM) expõem interface **assíncrona**; o **domínio permanece
síncrono e puro** (funções de métrica não fazem I/O). A orquestração ([[agente-orquestrador]])
coordena o async nas bordas.

## Alternativas consideradas
- Tudo síncrono — simples, mas desperdiça paralelismo de I/O.
- Async no domínio inteiro — contamina funções puras sem ganho ([[arquitetura]]).

## Consequências
- Possível buscar notícias e preparar dados concorrentemente.
- Fronteira async/sync fica explícita e testável.

## Relacionadas
[[agente-orquestrador]] · [[qualidade-governanca]] · [[arquitetura]]
