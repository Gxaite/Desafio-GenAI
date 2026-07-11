---
tags: [arquitetura, estrutura]
atualizado: 2026-07-09
---

# Estrutura de Projeto (Single Responsibility)

Monorepo **Docker multi-serviço** ([[containerizacao]]), pastas por serviço, cada uma com
seu Dockerfile. Dentro do `backend`, o núcleo segue **hexagonal** ([[principios]]).
**Cada arquivo tem uma responsabilidade única.**

```
Desafio-GenAI/
├── docker-compose.yml        # orquestra backend + dados + postgres + grafana
├── .env.example              # contrato de config (o .env real é gitignored)
├── justfile                  # tarefas: up, etl, test, lint
├── .github/workflows/ci.yml  # lint + type + test → [[qualidade-tooling]]
├── data/                     # raw/reference/interim/processed → ver data/README.md
├── docs/                     # diagrama conceitual (PDF)
├── vault/                    # este cérebro
│
├── grafana/                  # ── serviço grafana (provisioning-as-code) ──
│   └── provisioning/{datasources,dashboards}/   # → [[visualizacao-bi]]
│
├── dados/                    # ── serviço ETL (job) ──
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/etl/
│   │   ├── extract.py            # ler CSV (delimitador ';', encoding latin-1)
│   │   ├── clean.py              # limpeza + anonimização → [[dados-sensiveis]]
│   │   ├── dedupe.py             # unir 2025+2026 sem duplicar (casos de virada de ano)
│   │   └── load.py               # carregar marts no Postgres → [[camada-dados]]
│   └── tests/
│
└── backend/                  # ── serviço FastAPI + agente (núcleo hexagonal) ──
    ├── Dockerfile
    ├── pyproject.toml
    ├── tests/{unit,integration}/
    └── src/srag_report/
        ├── domain/               # NÚCLEO puro (sem I/O, sem frameworks)
        │   ├── models.py             # Periodo, Metrica, Noticia, Relatorio (pydantic)
        │   ├── metrics/              # 1 função pura por métrica → [[metricas]]
        │   │   ├── incidencia.py · mortalidade.py · uti.py · vacinacao.py
        │   ├── ports.py              # Protocols: RepositorioDados, FonteNoticias, ModeloLLM, Publicador
        │   └── errors.py             # exceções de domínio → [[tratamento-erros]]
        ├── application/          # orquestração (depende só de ports)
        │   ├── use_cases/gerar_relatorio.py
        │   ├── orchestration/        # LangGraph confinado → [[agente-orquestrador]]
        │   │   ├── graph.py · state.py · nodes/
        │   └── guardrails/           # → [[guardrails]]
        ├── infrastructure/       # ADAPTERS (implementam as ports)
        │   ├── data/postgres_repo.py     # RepositorioDados sobre Postgres → [[adr-0006-duckdb]]
        │   ├── news/newsapi_client.py    # → [[adr-0002-fonte-noticias]]
        │   ├── llm/openrouter_client.py  # → [[adr-0001-provedor-llm]]
        │   ├── report/{charts.py,pdf_renderer.py}  # matplotlib + WeasyPrint
        │   └── resilience/               # retry/timeout/circuit breaker → [[resiliencia]]
        ├── observability/        # logging.py · tracing.py · audit.py → [[observabilidade]]
        ├── config/settings.py    # pydantic-settings (lê o .env)
        ├── api/                  # FastAPI (rotas, /health)
        └── cli.py                # composition root + entrypoint
```

## Regras de dependência (impostas no CI via import-linter)
- `domain/` **não importa** `application/`, `infrastructure/` nem libs de I/O.
- `application/` importa só `domain` (ports/models), **nunca** `infrastructure`.
- Ligações concretas montadas no `cli.py`/`api/` (injeção de dependência).
- `dados` e `backend` **não compartilham código**: o contrato entre eles é o **schema do
  Postgres** (bounded contexts) → ver [[containerizacao]].

## Ligações
[[principios]] · [[containerizacao]] · [[visao-geral]]
