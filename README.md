# Desafio GenAI · Relatório Automatizado de SRAG

![coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
![tests](https://img.shields.io/badge/pytest-29%20passing-brightgreen)
![dbt tests](https://img.shields.io/badge/dbt%20tests-34%20passing-brightgreen)
![SonarQube](https://img.shields.io/badge/SonarQube-0%20bugs%20%C2%B7%200%20vulns-brightgreen)
![arch](https://img.shields.io/badge/arquitetura-hexagonal%20%2B%20medallion-blue)

Agente de IA generativa (LangGraph) que consulta dados reais de SRAG (Open DATASUS / SIVEP-Gripe)
e notícias em tempo real para gerar um relatório automatizado em PDF, com as métricas exigidas,
dois gráficos e uma narrativa de contexto. Toda a solução roda em Docker.

Contexto: PoC para a Indicium HealthCare Inc. avaliar uma solução que ajude profissionais de
saúde a entender a severidade e o avanço de surtos de SRAG.

## Sumário

1. [Como rodar](#como-rodar)
2. [Interfaces](#interfaces)
3. [Arquitetura](#arquitetura)
4. [Métricas e gráficos](#métricas-e-gráficos)
5. [Governança, guardrails e dados sensíveis](#governança-guardrails-e-dados-sensíveis)
6. [Qualidade](#qualidade)
7. [Stack e documentação](#stack-e-documentação)

## Como rodar

Pré-requisitos: **Docker** (com integração WSL2 ativa, se aplicável) e as chaves de API do
**OpenRouter** (LLM) e do **NewsAPI** (notícias).

```bash
# 1. Configuração (o .env é gitignored; nenhuma chave vai para o repositório)
cp .env.example .env
#    preencha OPENROUTER_API_KEY e NEWSAPI_KEY no .env

# 2. Suba a stack (Postgres, backend/agente, Grafana)
docker compose up -d postgres backend grafana

# 3. Rode o ETL (bronze -> silver -> gold + testes de dados)
docker compose --profile etl run --rm dados
```

No passo 3, se não houver CSV em `data/raw/srag/`, o ETL **baixa os dados automaticamente** do
Open DATASUS (S3 público, snapshot versionado). Ou seja, o projeto roda a partir de um clone
limpo, sem precisar do arquivo de 554 MB no repositório.

Em seguida, abra o **hub** em **http://localhost:8000/**.

## Interfaces

| Interface | URL | Descrição |
|---|---|---|
| Hub | http://localhost:8000/ | Ponto de entrada: métricas ao vivo, geração de relatório em tempo real, trilha da última execução e explorador de notícias (histograma por mês, filtros por fonte e período) |
| API (Swagger) | http://localhost:8000/docs | Documentação interativa dos endpoints |
| Grafana | http://localhost:3000 | Dashboard interativo (usuário `admin`, senha em `GF_SECURITY_ADMIN_PASSWORD`) |

Endpoints principais:

| Endpoint | Função |
|---|---|
| `POST /relatorio` | Gera o relatório PDF completo (bloqueante) |
| `GET /relatorio/stream` | Gera o relatório emitindo o progresso do agente nó a nó (SSE) |
| `GET /metricas` | As quatro métricas em JSON |
| `GET /noticias` | Histórico de notícias, filtrável por `fonte` e `dias` (período) |
| `GET /noticias/serie` e `/noticias/fontes` | Volume mensal (histograma) e fontes distintas do histórico |
| `POST /noticias/buscar` | Coleta notícias (10 consultas) e persiste no histórico; retorna quantas são novas |
| `GET /agente/grafo` | Página do fluxo do agente (fonte Mermaid em `?format=mermaid`) |
| `GET /auditoria/execucoes` e `/{run_id}` | Execuções do agente e a trilha detalhada (tempos, fontes) |
| `GET /health`, `/health/db` | Liveness e readiness |

## Arquitetura

Princípio-guia: o LLM orquestra e explica, o Python calcula. Todas as métricas são SQL/Python
determinístico; o LLM apenas narra sobre números já apurados, sem alucinar. O núcleo do backend
segue **hexagonal (Ports & Adapters)** e os dados seguem **medallion** (bronze, silver, gold).

```mermaid
flowchart TD
    subgraph fontes["Fontes"]
        CSV[("CSV Open DATASUS<br/>SIVEP-Gripe")]
        NEWS[["NewsAPI<br/>tempo real"]]
        LLM[["Claude via OpenRouter"]]
    end
    subgraph dados["Servico dados · ETL medallion (dbt)"]
        BRONZE[("bronze<br/>landing bruto")]
        SILVER[("silver<br/>limpo + dedup")]
        GOLD[("gold<br/>star schema")]
        CSV --> BRONZE --> SILVER --> GOLD
    end
    subgraph backend["Servico backend · Agente Orquestrador (LangGraph)"]
        direction LR
        T1["tool<br/>calcular_metricas"]
        T2["tool<br/>dados_grafico"]
        T3["tool<br/>buscar_noticias"]
        NARR["no narrativa<br/>(LLM)"]
        REL["montar relatorio<br/>Plotly + WeasyPrint"]
        T1 --> T2 --> T3 --> NARR --> REL
    end
    GOLD --> T1
    GOLD --> T2
    NEWS --> T3
    LLM --> NARR
    REL --> PDF[["Relatorio PDF"]]
    GOLD --> GRAFANA[["Grafana"]]
    AUDIT[("Auditoria<br/>trilha por run_id")]
    backend -.registra.-> AUDIT
```

Versão em PDF (entregável): [`docs/diagrama-conceitual.pdf`](docs/diagrama-conceitual.pdf),
reproduzível com `uv run --with weasyprint python docs/gerar_diagrama.py`.

Camadas de código do `backend`: `domain/` (puro, sem I/O), `application/` (casos de uso,
orquestração LangGraph e guardrails), `infrastructure/` (adapters de Postgres, NewsAPI,
OpenRouter e relatório), além de `api/` e `composition.py` (composition root). As fronteiras do
hexágono são impostas no CI pelo `import-linter`. Detalhes em
[`vault/arquitetura.md`](vault/arquitetura.md) e nas ADRs em [`vault/decisoes/`](vault/decisoes).

Serviços em Docker:

| Serviço | Papel |
|---|---|
| `postgres` | Store analítico servido (camada gold) |
| `dados` | Job de ETL: EL em Python (bronze) e **dbt** (staging, intermediate, marts em star schema) com testes de dados |
| `backend` | FastAPI, agente LangGraph, tools e geração do PDF |
| `grafana` | Dashboard interativo (lê a gold) |

## Métricas e gráficos

| Métrica | Definição | Coluna |
|---|---|---|
| Taxa de aumento de casos | Variação percentual vs. período anterior de igual duração | `DT_SIN_PRI` |
| Taxa de mortalidade | Óbitos (`EVOLUCAO=2`) sobre casos com desfecho conhecido | `EVOLUCAO` |
| Taxa de ocupação de UTI | Proxy: casos com `UTI=1` sobre casos com UTI conhecida | `UTI` |
| Taxa de vacinação | Proxy: casos vacinados sobre casos com status conhecido | `VACINA_COV` |

UTI e vacinação são proxies explícitos, pois a base traz status por caso, não leitos totais nem
cobertura populacional. A premissa é documentada no relatório e os denominadores usam apenas
valores conhecidos (1 ou 2). Gráficos: casos diários (30 dias) e casos mensais (12 meses).

## Governança, guardrails e dados sensíveis

- **Governança e transparência:** cada execução recebe um `run_id` e grava uma trilha de
  auditoria (nós, tipos, durações, métricas e fontes) no Postgres, visível no hub e no Grafana.
  O relatório traz rodapé com modelo, fontes e timestamp. As ADRs registram o porquê de cada decisão.
- **Guardrails:** validação de entrada com pydantic, grounding (o LLM só narra sobre os números
  das tools), filtro de relevância das notícias, validação de saída e falha explícita ou `N/A`.
- **Dados sensíveis (LGPD):** minimização (só as colunas necessárias entram no bronze) e apenas
  agregados são servidos (camada gold); nenhum dado a nível de indivíduo sai do banco.
- **Resiliência (fail-fast, sem fallback):** timeouts e retry com backoff em erros transitórios;
  esgotados os retries, a falha sobe como erro tipado e a API responde **503** (ou emite evento
  de erro no stream). Não há relatório silenciosamente degradado: se dados, notícias ou LLM
  falharem, a execução falha explicitamente, em vez de entregar um relatório que aparente estar
  completo. Ver [`adr-0010`](vault/decisoes/adr-0010-resiliencia.md).

## Qualidade

Portões automatizados, executados no CI a cada push:

- `ruff` (lint e formatação), `mypy --strict` (tipagem) e `import-linter` (fronteiras do hexágono)
- `pytest` com cobertura mínima de 85% (atual ~99%) e casos de borda
- `bandit` (segurança) e `sqlfluff` (lint de SQL do dbt)

```bash
cd backend && uv run --extra dev pytest
uv run --extra dev ruff check . && uv run --extra dev mypy src
uv run --extra dev lint-imports && uv run --extra dev bandit -r src -q
```

**SonarQube** (dashboard de qualidade, opcional, profile `quality`):

```bash
docker compose --profile quality up -d sonar-db sonarqube   # http://localhost:9000
cd backend && uv run --extra dev pytest                     # gera coverage.xml
SONAR_TOKEN=<token> docker compose --profile quality run --rm sonar-scanner
```

Última análise: cobertura 99,4%, 0 bugs, 0 vulnerabilidades, 0 hotspots, 0% duplicação. Os
adapters de I/O ficam fora da métrica de cobertura (são cobertos por testes de integração).

## Stack e documentação

Python, Docker, Postgres, dbt (medallion), FastAPI, LangGraph, Claude via OpenRouter, NewsAPI,
Plotly, WeasyPrint, Grafana, `structlog`, `tenacity`, e `uv`/`ruff`/`mypy`/`pytest`. Tracing de
LLM opcional via OpenRouter Broadcast para o LangSmith (configurado no painel do OpenRouter).

Documentação viva em [`vault/`](vault/README.md) (arquitetura, domínio, ADRs, princípios SOLID).
Dados em [`data/README.md`](data/README.md) e ETL em [`dados/README.md`](dados/README.md).
