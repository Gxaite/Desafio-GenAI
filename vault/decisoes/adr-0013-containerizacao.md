---
tags: [decisao, adr, infra, docker]
status: aceito
data: 2026-07-09
---

# ADR-0013 — Containerização com Docker (compose + .env)

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
A solução deve rodar de forma reprodutível, com serviços isolados e parametrizados,
desde o início. Também alinha com a experiência em Docker valorizada no contexto.

## Decisão
**Docker desde o dia 1**, com um `docker-compose.yml` na **raiz** orquestrando os
serviços, cada um com seu **Dockerfile** em sua pasta, e **tudo parametrizado via um
`.env` único** na raiz. Topologia em [[arquitetura]]:

- `backend` — FastAPI + núcleo hexagonal + agente (serviço único; não há divisão ai/backend).
- `dados` — job de ETL (roda até concluir, carrega marts no Postgres).
- `postgres` — store analítico ([[adr-0006-duckdb]]).
- `grafana` — dashboards ([[adr-0014-grafana]]).

## Alternativas consideradas
- Rodar local sem containers — menos reprodutível.
- Separar `backend` e `ai` — descartado; agrega latência/complexidade sem ganho na PoC.

## Consequências
- Ambiente reprodutível e isolado; `.env` como única fonte de parâmetros/segredos ([[qualidade-governanca]]).
- Boas práticas: multi-stage, imagem slim, usuário não-root, healthchecks, `.dockerignore`.
- Orquestração básica via compose (K8s fica como evolução futura, fora de escopo).

## Relacionadas
[[arquitetura]] · [[adr-0006-duckdb]] · [[adr-0014-grafana]] · [[adr-0009-tooling-uv-ruff-mypy]]
