# Serviço `dados` — ETL medallion (EL + dbt)

Job que transforma o CSV bruto do Open DATASUS (SIVEP-Gripe) nos marts servidos ao backend e
ao Grafana. Arquitetura **medallion** com **uma pasta dbt por camada** (`bronze/`, `silver/`,
`gold/`), editável isoladamente.

```
CSV (data/raw)
   │  EL em Python (psycopg COPY) — carrega só ~6 colunas (minimização LGPD)
   ▼
🥉 bronze.srag_raw            landing bruto (texto) + arquivo_origem
   │  dbt
🥈 silver.silver_srag_casos   tipa (data ISO→date), normaliza vazios, dedup e flags de negócio (table)
   ▼
🥇 gold.dim_uf · gold.dim_data      dimensões (UF via seed com região; calendário)
🥇 gold.fct_srag_diario             fato: grão (dia, UF), medidas aditivas, FKs
🥇 gold.gold_mart_srag_diario       view de serviço (contrato do backend/Grafana)
```

## Estrutura

| Caminho | Papel |
|---|---|
| `src/srag_etl/` | EL em Python: lê os CSVs, `COPY` para `bronze.srag_raw`, orquestra o `dbt build` |
| `dbt/models/bronze/` | `_bronze__sources.yml` — declara a landing bruta (carregada pelo EL) |
| `dbt/models/silver/` | `silver_srag_casos` — limpeza/tipagem/dedup/flags (table) |
| `dbt/models/gold/` | `dim_*`, `fct_*` e a view de serviço (star schema) |
| `dbt/seeds/` | `seed_uf.csv` — mapa UF → nome/região (fonte da `dim_uf`) |
| `dbt/tests/` | testes singulares (grão único, coerência de medidas) |

## Como rodar

**Em Docker (recomendado):**
```bash
docker compose --profile etl run --rm dados   # EL (bronze) + dbt build (silver/gold + testes)
```

**Local (dev), com o Postgres do compose de pé:**
```bash
cd dados
POSTGRES_HOST=localhost SRAG_RAW_DIR="$PWD/../data/raw/srag" \
  uv run --with 'psycopg[binary]' --with dbt-postgres --with structlog --with pydantic-settings \
  python -m srag_etl
```

## Qualidade de dados (dbt tests)
`not_null`, `unique`, `accepted_values`, **relationships** (fato → dimensões), grão único do
fato e coerência de medidas (não-negativas; sub-contagens ≤ total). Rodam no `dbt build`.

## Documentação e lineage
```bash
cd dados/dbt && dbt docs generate && dbt docs serve   # catálogo + grafo de lineage
```
As `exposures` declaram o relatório PDF e o dashboard Grafana como consumidores da gold.
Descrições de modelo/coluna são persistidas como comentários no Postgres (`persist_docs`).

## Princípios
- **Minimização (LGPD):** só as colunas necessárias entram no bronze; **só a gold é servida**.
- **Idempotência:** `TRUNCATE`+recarrega bronze; `dbt build` reconstrói silver/gold.
- **Bounded context:** `dados` e `backend` não compartilham código — o contrato é o schema gold.

Detalhes de decisão: `../vault/camada-dados.md`, `../vault/decisoes/adr-0015-dbt-medallion.md`,
`../vault/decisoes/adr-0016-modelagem-dimensional.md`.
