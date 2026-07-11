---
tags: [planejamento, tecnologia]
atualizado: 2026-07-09
---

# Stack Tecnológica

| Camada | Ferramenta | Motivo | Nota |
|---|---|---|---|
| Orquestração de containers | **Docker + docker-compose** | reprodutível, isolado, parametrizado | [[adr-0013-containerizacao]], [[containerizacao]] |
| Store analítico | **Postgres 16** | banco servido, multi-serviço, datasource nativo do Grafana | [[adr-0006-duckdb]] |
| Transformação (ETL) | **DuckDB + pandas** (em memória) | crunch rápido do CSV de 194 colunas → marts no Postgres | [[camada-dados]] |
| API + agente | **FastAPI** + `langgraph` + `langchain-openai` | serviço `backend` único, grafo auditável | [[adr-0005-langgraph]], [[adr-0008-arquitetura-hexagonal]] |
| LLM | Claude via **OpenRouter** (`ChatOpenAI` + `base_url`) | flexível, troca por config | [[adr-0001-provedor-llm]] |
| Validação/tools | `pydantic` | schemas tipados = guardrails | [[guardrails]] |
| Gráficos (relatório) | `matplotlib` | os 2 gráficos exigidos no PDF | [[geracao-relatorio]] |
| Dashboard (bônus) | **Grafana** | séries temporais, provisioning-as-code | [[adr-0014-grafana]], [[visualizacao-bi]] |
| Notícias | `requests` / `newsapi-python` | NewsAPI | [[adr-0002-fonte-noticias]] |
| Relatório | Markdown → **WeasyPrint** | PDF final | [[geracao-relatorio]] |
| Resiliência | `tenacity` | retries/backoff/circuit breaker | [[resiliencia]] |
| Observabilidade | `structlog` + OpenTelemetry | logs JSON + tracing + auditoria | [[observabilidade]] |
| Config/segredos | `pydantic-settings` + **`.env` único** | 12-factor, nada no código | [[dados-sensiveis]] |
| Qualidade | **uv · ruff · mypy · pytest · import-linter · pre-commit · GitHub Actions** | portões automatizados | [[qualidade-tooling]] |

## Modelos (OpenRouter)
- **Haiku 4.5** → orquestração/decisão (rápido e barato).
- **Sonnet 5** → narrativa final do relatório.
- Slugs exatos do OpenRouter a confirmar ao codar. Ver [[adr-0001-provedor-llm]].

## Fora de escopo (não confundir com specs da vaga)
Frontend React/TS, RAG com vector store, Kubernetes, Kafka/SQS — **não** são requisitos
do desafio. Ver a memória de foco e [[adr-0014-grafana]].
