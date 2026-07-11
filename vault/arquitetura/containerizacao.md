---
tags: [arquitetura, infra, docker]
atualizado: 2026-07-09
---

# Containerização

Topologia Docker da solução. Decisão em [[adr-0013-containerizacao]]. Layout físico em
[[estrutura-projeto]].

## Serviços (docker-compose na raiz)

| Serviço | Base | Papel | Depende de |
|---|---|---|---|
| `postgres` | `postgres:16` | store analítico ([[adr-0006-duckdb]]) | — |
| `dados` | build `./dados` | **job** de ETL: transforma (DuckDB/pandas em memória) e carrega marts no Postgres | `postgres` (healthy) |
| `backend` | build `./backend` | FastAPI + núcleo hexagonal + agente ([[agente-orquestrador]]) | `postgres` (healthy), `dados` (concluído) |
| `grafana` | `grafana/grafana` | dashboards ([[visualizacao-bi]]) | `postgres` |

```
        .env (raiz) ── parametriza tudo
           │
  ┌────────┼─────────────────────────────┐
  │        │                              │
[dados]→ carrega → [postgres] ←lê── [backend] (API + agente)
 (job)                  ▲                   │
                        └──── lê ── [grafana] (dashboards)
```

## Volumes
- `./data/raw` → montado **read-only** no `dados` (fonte imutável).
- `pgdata` → volume nomeado para persistir o Postgres.
- `./grafana/provisioning` → datasources + dashboards como código.

## Orquestração
- **Healthchecks**: `pg_isready` no Postgres; `/health` no backend.
- **depends_on** com `condition: service_healthy` / `service_completed_successfully`
  (o `backend` só sobe após o ETL concluir).
- **Profiles**: o job `dados` pode rodar sob demanda (ex.: `docker compose --profile etl up dados`).

## Parametrização (.env único)
Todos os parâmetros e segredos ([[dados-sensiveis]]): `POSTGRES_*`, `OPENROUTER_API_KEY`,
`OPENROUTER_BASE_URL`, `OPENROUTER_MODEL_*`, `NEWSAPI_KEY`, `BACKEND_PORT`, `GRAFANA_PORT`,
`GF_SECURITY_ADMIN_*`, `LOG_LEVEL`. Versionamos apenas o `.env.example`.

## Boas práticas de imagem
Multi-stage (builder + runtime), base **slim**, **uv** para deps, usuário **não-root**,
`.dockerignore` por serviço, versões fixadas. Ver [[qualidade-tooling]].

## Ligações
[[adr-0013-containerizacao]] · [[estrutura-projeto]] · [[adr-0006-duckdb]] · [[visualizacao-bi]]
