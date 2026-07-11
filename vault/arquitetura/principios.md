---
tags: [arquitetura, principios]
atualizado: 2026-07-09
---

# Princípios de Arquitetura

Fundamentos inegociáveis do projeto. A meta é ser **projeto-referência**: moderno,
robusto, resiliente e com responsabilidade única bem distribuída.

## 1. Arquitetura Hexagonal (Ports & Adapters)
Decisão em [[adr-0008-arquitetura-hexagonal]]. O **domínio não conhece frameworks**.
LangGraph, Postgres, NewsAPI e OpenRouter são **adapters** plugados em **ports** (interfaces).

```
        Interface (CLI)
              │
        Application (casos de uso + orquestração)
              │  depende de →  Ports (Protocols)
        Domain (regras puras)  ← núcleo, zero I/O
              ▲  implementados por ↓
        Infrastructure (adapters: dados, notícias, llm, relatório)
```

## 2. SOLID, com foco em SRP e DIP
- **SRP** — um arquivo, uma razão para mudar. Cada métrica, cada adapter, isolados.
- **DIP** — camadas de cima dependem de abstrações ([[camada-tools|ports]]), nunca de SDKs concretos.

## 3. Domínio puro e determinístico
Regras de negócio ([[metricas]]) são **funções puras, sem I/O e sem estado global** —
testáveis sem mocks pesados. Reforça [[adr-0004-llm-orquestra-python-calcula]].

## 4. 12-Factor & Config explícita
Configuração e segredos por ambiente (`.env`), nunca no código ([[dados-sensiveis]]).
Dependências explícitas e injetadas (composition root no `cli.py`).

## 5. Fail-fast e fronteiras claras
Erros de infraestrutura são convertidos em erros de domínio tipados na fronteira
([[tratamento-erros]]). Nada de `except` silencioso.

## 6. Resiliência como requisito, não enfeite
Timeouts, retries e degradação graciosa em toda borda externa ([[resiliencia]]).

## 7. Observável por construção
Log estruturado + tracing + trilha de auditoria desde o dia 1 ([[observabilidade]], [[governanca-auditoria]]).

## Ligações
[[estrutura-projeto]] · [[qualidade-tooling]] · [[visao-geral]]
