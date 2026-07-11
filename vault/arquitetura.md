# Arquitetura

Princípio-guia: **o LLM orquestra e explica; o Python calcula** ([[adr-0004-llm-orquestra-python-calcula]]).
Núcleo hexagonal ([[adr-0008-arquitetura-hexagonal]]), tudo em Docker ([[adr-0013-containerizacao]]).

## Visão em 4 camadas

```
┌─────────────────────────────────────────────────────────┐
│  1. DADOS        → [[camada-dados]]                      │
│     CSV DATASUS → limpeza → marts no Postgres            │
│  2. TOOLS        → [[camada-tools]]                      │
│     calcular_metricas · dados_grafico · buscar_noticias  │
│  3. AGENTE       → [[agente-orquestrador]]               │
│     grafo LangGraph, cada nó logado                      │
│  4. RELATÓRIO    → [[geracao-relatorio]]                 │
│     métricas + 2 gráficos + narrativa → PDF              │
│  ⟳ TRANSVERSAL: [[qualidade-governanca]]                 │
└─────────────────────────────────────────────────────────┘
```

**Fluxo do agente (MVP linear):**
`calcular_metricas` → `dados_grafico` → `buscar_noticias` → `narrar (LLM)` → `montar relatório`.
Na PoC completa o grafo ganha arestas condicionais (re-consultar dado ausente) e validação
entre nós — ver [[agente-orquestrador]].

O **diagrama conceitual** exigido pelo desafio (Orquestrador + Tools + LLM + Banco + Notícias)
deriva desta visão e é entregue em PDF.

## Princípios

- **Hexagonal (Ports & Adapters)** — o domínio não conhece frameworks. LangGraph, Postgres,
  NewsAPI e OpenRouter são *adapters* plugados em *ports* (Protocols).
- **SOLID (SRP + DIP)** — um arquivo, uma razão para mudar; camadas de cima dependem de
  abstrações, nunca de SDKs concretos.
- **Domínio puro e determinístico** — regras de negócio ([[metricas]]) são funções puras, sem
  I/O nem estado global, testáveis sem mocks pesados.
- **12-Factor** — config e segredos por ambiente (`.env`), injetados no composition root (`cli.py`).
- **Fail-fast** — erros de infra viram erros de domínio tipados na fronteira; sem `except` nu
  (ver [[qualidade-governanca]]).
- **Resiliência e observabilidade por construção** — desde o dia 1, não como enfeite.

```
        Interface (CLI/API)
              │
        Application (casos de uso + orquestração)  → depende de Ports (Protocols)
              │
        Domain (regras puras)   ← núcleo, zero I/O
              ▲  implementado por ↓
        Infrastructure (adapters: dados, notícias, llm, relatório)
```

## Estrutura de projeto

Monorepo Docker multi-serviço; pastas por serviço, cada uma com seu Dockerfile. Cada arquivo
tem responsabilidade única.

```
Desafio-GenAI/
├── docker-compose.yml        # orquestra backend + dados + postgres + grafana
├── .env.example              # contrato de config (o .env real é gitignored)
├── justfile                  # tarefas: up, etl, test, lint
├── .github/workflows/ci.yml  # lint + type + test
├── data/                     # raw/reference/interim/processed → ver data/README.md
├── docs/                     # diagrama conceitual (PDF)
├── grafana/provisioning/     # ── serviço grafana (datasources + dashboards como código) ──
│
├── dados/                    # ── serviço ETL medallion (job) ──
│   ├── src/srag_etl/         # EL: CSV → bronze (Python) + orquestra o dbt
│   └── dbt/                   # transformação → [[camada-dados]]
│       ├── models/{staging,intermediate,marts}/   # silver → gold (star schema)
│       └── seeds/            # dim_uf (código → nome/região)
│
└── backend/                  # ── serviço FastAPI + agente (núcleo hexagonal) ──
    └── src/srag_report/
        ├── domain/               # NÚCLEO puro (sem I/O, sem frameworks)
        │   ├── models.py             # Periodo, Metrica, Noticia, Relatorio (pydantic)
        │   ├── metrics/              # 1 função pura por métrica → [[metricas]]
        │   ├── ports.py              # Protocols: RepositorioDados, FonteNoticias, ModeloLLM, Publicador
        │   └── errors.py             # exceções de domínio
        ├── application/          # orquestração (depende só de ports)
        │   ├── use_cases/gerar_relatorio.py
        │   ├── orchestration/        # LangGraph confinado → [[agente-orquestrador]]
        │   └── guardrails/           # → [[qualidade-governanca]]
        ├── infrastructure/       # ADAPTERS (implementam as ports)
        │   ├── data/postgres_repo.py     # RepositorioDados sobre Postgres
        │   ├── news/newsapi_client.py    # → [[adr-0002-fonte-noticias]]
        │   ├── llm/openrouter_client.py  # → [[adr-0001-provedor-llm]]
        │   ├── report/{charts.py,pdf_renderer.py}  # Plotly + WeasyPrint
        │   └── resilience/               # retry/timeout/circuit breaker
        ├── observability/        # logging.py · tracing.py · audit.py
        ├── config/settings.py    # pydantic-settings (lê o .env)
        ├── api/                  # FastAPI (rotas, /health)
        └── cli.py                # composition root + entrypoint
```

**Regras de dependência (impostas no CI via import-linter):**
- `domain/` não importa `application/`, `infrastructure/` nem libs de I/O.
- `application/` importa só `domain` (ports/models), nunca `infrastructure`.
- Ligações concretas montadas no `cli.py`/`api/` (injeção de dependência).
- `dados` e `backend` **não compartilham código**: o contrato entre eles é o **schema do
  Postgres** (bounded contexts).

## Containerização

Serviços no `docker-compose.yml` da raiz, `.env` único, healthchecks e `depends_on`.

| Serviço | Base | Papel | Depende de |
|---|---|---|---|
| `postgres` | `postgres:16` | store analítico ([[adr-0006-duckdb]]) | — |
| `dados` | build `./dados` | **job** de ETL medallion: EL (Python) + dbt → serve o mart gold | `postgres` (healthy) |
| `backend` | build `./backend` | FastAPI + núcleo hexagonal + agente | `postgres` (healthy), `dados` (concluído) |
| `grafana` | `grafana/grafana` | dashboards (bônus, [[adr-0014-grafana]]) | `postgres` |

```
        .env (raiz) ── parametriza tudo
  ┌────────────────────────────────────┐
[dados]→ carrega → [postgres] ←lê── [backend] (API + agente)
 (job)                  ▲                
                        └──── lê ── [grafana] (dashboards)
```

- **Volumes:** `./data/raw` montado **read-only** no `dados` (fonte imutável); `pgdata` persiste
  o Postgres; `./grafana/provisioning` = datasources + dashboards como código.
- **Orquestração:** healthchecks (`pg_isready`, `/health`); `depends_on` com `service_healthy` /
  `service_completed_successfully`; o job `dados` roda sob demanda (profile `etl`).
- **Imagem:** multi-stage (builder + runtime), base slim, `uv` para deps, usuário não-root,
  `.dockerignore` por serviço, versões fixadas.

## Stack

| Camada | Ferramenta | Motivo |
|---|---|---|
| Containers | Docker + docker-compose | reprodutível, isolado, parametrizado |
| Store analítico | **Postgres 16** | banco servido, datasource nativo do Grafana |
| Transformação (ETL) | **EL Python + dbt** (medallion) | bronze→silver→gold no Postgres, com testes de dados ([[adr-0015-dbt-medallion]]) |
| API + agente | **FastAPI** + `langgraph` + `langchain-openai` | serviço único, grafo auditável |
| LLM | Claude via **OpenRouter** (`ChatOpenAI` + `base_url`) | flexível, troca por config |
| Validação/tools | `pydantic` | schemas tipados = guardrails |
| Gráficos / Relatório | **Plotly** (kaleido) → HTML → **WeasyPrint** | os 2 gráficos + PDF final |
| Notícias | `requests` / `newsapi-python` | NewsAPI ([[adr-0002-fonte-noticias]]) |
| Resiliência | `tenacity` | retries/backoff/circuit breaker |
| Observabilidade | `structlog` + OpenTelemetry | logs JSON + tracing + auditoria |
| Config/segredos | `pydantic-settings` + `.env` único | 12-factor, nada no código |
| Qualidade | **uv · ruff · mypy · pytest · import-linter · pre-commit · GitHub Actions** | portões automatizados |
| Dashboard (bônus) | **Grafana** | séries temporais, provisioning-as-code |

**Modelos (OpenRouter):** Haiku 4.5 para orquestração (rápido/barato), Sonnet 5 para a narrativa
final. Slugs exatos a confirmar ao codar ([[adr-0001-provedor-llm]]).

**Fora de escopo** (não são requisitos do desafio): frontend React/TS, RAG com vector store,
Kubernetes, Kafka/SQS.

## Decisões que sustentam esta arquitetura

Ver [[decisoes/adr-0001-provedor-llm|todas as ADRs]] — em especial hexagonal (0008),
LLM-orquestra-Python-calcula (0004), LangGraph (0005), Postgres (0006) e containerização (0013).
