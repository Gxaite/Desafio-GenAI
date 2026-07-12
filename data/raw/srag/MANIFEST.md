# MANIFEST — Dados brutos SRAG (SIVEP-Gripe)

Registro de **proveniência** dos dados brutos. `raw/` é **imutável**: nunca editar o
conteúdo destes arquivos; qualquer transformação vive em `interim/`, `processed/` ou no
Postgres. Ver `../../README.md`.

## Origem
- **Fonte:** Open DATASUS — Banco de dados da SRAG (SIVEP-Gripe), 2019 a 2026.
- **Portal:** https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024 (dataset "SRAG 2019 a 2026").
- **Licença:** dados públicos (Lei de Acesso à Informação / DATASUS).
- **Extração:** 2026-07-06.

## Download direto (S3 público)
O ETL **baixa destas URLs** quando não há CSV local (config `SRAG_CSV_URLS`):
- 2025: `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-06-07-2026.csv`
- 2026: `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2026/INFLUD26-06-07-2026.csv`
- Dicionário: `.../SRAG/dicionario-de-dados-2019-a-2025.pdf` · Ficha: `.../SRAG/ficha-de-notificacao-2025.pdf`

## Arquivos

| Nome atual | Nome original | Ano | Extração | Tamanho (bytes) |
|---|---|---|---|---|
| `srag-2025-extracao-2026-07-06.csv` | `INFLUD25-06-07-2026.csv` | 2025 | 2026-07-06 | 381.864.580 |
| `srag-2026-extracao-2026-07-06.csv` | `INFLUD26-06-07-2026.csv` | 2026 | 2026-07-06 | 172.616.869 |

> `INFLUD` = prefixo dos arquivos do SIVEP-Gripe; sufixo `DD-MM-AAAA` = data de extração.

## Características técnicas
- **Formato:** CSV, delimitador `;`, campos entre aspas.
- **Colunas:** 194.
- **Encoding:** **UTF-8** (confirmado na sondagem).
- **Documentação dos campos:** `../../reference/dicionario-de-dados-srag-2019-2025.pdf`.

## Convenção de nomes
`<dataset>-<ano>-extracao-<AAAA-MM-DD>.<ext>` — minúsculas, kebab-case, datas ISO 8601.
