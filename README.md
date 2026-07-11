# Desafio GenAI — Relatório Automatizado de SRAG

PoC de um **agente de IA generativa** que consulta dados reais de SRAG (Open DATASUS) e
notícias em tempo real para gerar um **relatório automatizado** com métricas e explicações.

> 🧠 **Todas as decisões e a arquitetura estão documentadas no [`vault/`](vault/README.md)**
> (segundo cérebro em notas interligadas). Comece por lá.

## Arquitetura (resumo)

Ver [`vault/arquitetura.md`](vault/arquitetura.md). Núcleo
hexagonal ([Ports & Adapters](vault/decisoes/adr-0008-arquitetura-hexagonal.md)); tudo
roda em **Docker**.

| Serviço | Papel |
|---|---|
| `postgres` | store analítico |
| `dados` | ETL (CSV → limpeza → marts no Postgres) |
| `backend` | FastAPI + agente LangGraph + tools |
| `grafana` | dashboards (bônus) |

## Como rodar

Pré-requisitos: **Docker** (com integração WSL ativada) e [`just`](https://github.com/casey/just) (opcional).

```bash
cp .env.example .env       # preencha OPENROUTER_API_KEY e NEWSAPI_KEY
just up                    # ou: docker compose up -d --build postgres backend grafana
curl localhost:8000/health # -> {"status":"ok"}
just etl                   # roda o ETL quando os dados estiverem em data/raw/srag/
```

- API: http://localhost:8000  · Grafana: http://localhost:3000
- Dados brutos: `data/` (ver [`data/README.md`](data/README.md)).

## Status
Em construção — ver o backlog de fases em [`vault/roadmap.md`](vault/roadmap.md).
