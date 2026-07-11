---
tags: [decisao, adr, arquitetura]
status: aceito
data: 2026-07-09
---

# ADR-0008 — Arquitetura Hexagonal (Ports & Adapters)

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
A meta é um projeto-referência: moderno, robusto, com responsabilidade única e trocável.
Precisamos isolar as regras de negócio dos frameworks (LangGraph, Postgres, NewsAPI, OpenRouter).

## Decisão
Adotar **Arquitetura Hexagonal**: um núcleo de **domínio puro** que define **ports**
(Protocols), com frameworks/serviços entrando como **adapters** de infraestrutura.
Camadas: domain → application → infrastructure/interface. Ver [[principios]] e [[estrutura-projeto]].

## Alternativas consideradas
- Arquitetura em camadas simples/MVC — menos isolamento, acopla domínio a I/O.
- Script monolítico — rápido, mas o oposto de "projeto-referência".

## Consequências
- Domínio testável sem mocks; adapters trocáveis (ex.: trocar NewsAPI ou LLM).
- Regras de dependência impostas no CI via `import-linter` ([[qualidade-tooling]]).
- Custo: mais arquivos e cerimônia — justificado pelo objetivo.

## Relacionadas
[[principios]] · [[estrutura-projeto]] · [[adr-0005-langgraph]] · [[adr-0004-llm-orquestra-python-calcula]]
