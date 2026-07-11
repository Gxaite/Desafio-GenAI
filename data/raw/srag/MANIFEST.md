# MANIFEST — Dados brutos SRAG (SIVEP-Gripe)

Registro de **proveniência** dos dados brutos. `raw/` é **imutável**: nunca editar o
conteúdo destes arquivos; qualquer transformação vive em `interim/`, `processed/` ou no
Postgres. Ver `../../README.md`.

## Origem
- **Fonte:** Open DATASUS — Banco de dados da SRAG (SIVEP-Gripe), 2019 a 2026.
- **URL:** https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024 (dataset "SRAG 2019 a 2026").
- **Licença:** dados públicos (Lei de Acesso à Informação / DATASUS).
- **Extração:** 2026-07-06.

## Arquivos

| Nome atual | Nome original | Ano | Extração | Tamanho |
|---|---|---|---|---|
| `srag-2025-extracao-2026-07-06.csv` | `INFLUD25-06-07-2026.csv` | 2025 | 2026-07-06 | ~382 MB |
| `srag-2026-extracao-2026-07-06.csv` | `INFLUD26-06-07-2026.csv` | 2026 | 2026-07-06 | ~173 MB |

> `INFLUD` = prefixo dos arquivos do SIVEP-Gripe; sufixo `DD-MM-AAAA` = data de extração.

## Características técnicas
- **Formato:** CSV, delimitador `;`.
- **Colunas:** 194.
- **Encoding:** provável **ISO-8859-1 (latin-1)** — confirmar no ETL.
- **Documentação dos campos:** `../../reference/dicionario-de-dados-srag-2019-2025.pdf`.

## Convenção de nomes
`<dataset>-<ano>-extracao-<AAAA-MM-DD>.<ext>` — minúsculas, kebab-case, datas ISO 8601.
