---
aliases: [Índice, Home, Cérebro]
tags: [indice, moc]
atualizado: 2026-07-09
---

# 🧠 Vault do Desafio GenAI — SRAG / DATASUS

Este vault é o **cérebro do projeto**: mantém decisões, arquitetura e conhecimento
de domínio em notas interligadas. Toda decisão relevante vira uma nota conectada,
servindo como trilha de auditoria viva (ver [[governanca-auditoria]]).

> Fonte do desafio: `../atividade_genAI.md`

## 🎯 Ponto de partida

- [[criterios-avaliacao]] — o "mapa do tesouro": onde investir esforço
- [[visao-geral]] — a arquitetura da solução em uma página
- [[fases]] — plano de implementação (MVP → PoC completa)

## 🏗️ Arquitetura

**Fundamentos:**
- [[principios]] — hexagonal, SOLID, 12-factor
- [[estrutura-projeto]] — layout `src/` com responsabilidade única
- [[resiliencia]] · [[observabilidade]] · [[tratamento-erros]] · [[qualidade-tooling]]
- [[containerizacao]] — Docker (compose + `.env`) · [[visualizacao-bi]] — Grafana

**Camadas e transversais:**
- [[visao-geral]]
- [[camada-dados]]
- [[camada-tools]]
- [[agente-orquestrador]]
- [[geracao-relatorio]]
- [[governanca-auditoria]]
- [[guardrails]]
- [[dados-sensiveis]]

## 🧬 Domínio

- [[srag-datasus]] — sobre a base de dados
- [[metricas]] — as 4 métricas + 2 gráficos exigidos

## 🗂️ Decisões (ADRs)

- [[adr-0001-provedor-llm]] — Claude via OpenRouter
- [[adr-0002-fonte-noticias]] — NewsAPI
- [[adr-0003-estrategia-mvp-primeiro]] — MVP antes da PoC completa
- [[adr-0004-llm-orquestra-python-calcula]] — princípio central
- [[adr-0005-langgraph]] — framework de orquestração
- [[adr-0006-duckdb]] — armazenamento analítico
- [[adr-0007-metricas-proxy]] — proxies de UTI e vacinação
- [[adr-0008-arquitetura-hexagonal]] — Ports & Adapters
- [[adr-0009-tooling-uv-ruff-mypy]] — portões de qualidade
- [[adr-0010-resiliencia]] — timeouts, retries, circuit breaker
- [[adr-0011-async-io]] — async nas bordas, domínio puro
- [[adr-0012-observabilidade]] — structlog + OTel + auditoria
- [[adr-0013-containerizacao]] — Docker (compose + `.env`)
- [[adr-0014-grafana]] — Grafana como dashboard

## 📐 Planejamento

- [[fases]]
- [[stack]]

## ✍️ Convenções

- Novas decisões usam [[template-adr]] e são numeradas em sequência.
- Conecte notas com `[[wikilink]]` sempre que houver relação.
- Datas em formato absoluto (`AAAA-MM-DD`).
