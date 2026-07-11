# `data/` — Organização dos Dados

Layout inspirado em convenções de projetos de dados de referência
(**Cookiecutter Data Science** + camadas estilo **medallion**: bronze → silver → gold).
Detalhes de arquitetura no vault: `../vault/arquitetura/camada-dados.md`.

## Camadas

| Pasta | Papel | Versionado? |
|---|---|---|
| `raw/` | **Bronze** — dados de origem, **imutáveis**. Proveniência em `raw/srag/MANIFEST.md` | ❌ (CSVs grandes) |
| `reference/` | Metadados: dicionário de dados e ficha de notificação | ✅ (PDFs pequenos) |
| `interim/` | **Silver** — intermediários do ETL (limpeza/anonimização) | ❌ (gerado) |
| `processed/` | **Gold** — marts prontos (também carregados no **Postgres**) | ❌ (gerado) |

## Princípios
- **`raw/` é imutável** — transformar sempre em cópias, nunca no original.
- **Marts servidos vivem no Postgres** (store analítico); os arquivos aqui são artefatos
  de pipeline, reprodutíveis a partir de `raw/`.
- **Nomes:** minúsculas, kebab-case, datas **ISO 8601** (`AAAA-MM-DD`), sortáveis.
- **Dados sensíveis**: microdados de saúde — ver `../vault/arquitetura/dados-sensiveis.md`.

## Convenção de nomes de arquivo
`<dataset>-<ano>-extracao-<AAAA-MM-DD>.<ext>`
Ex.: `srag-2026-extracao-2026-07-06.csv`
