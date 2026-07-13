<!-- GERADO por scripts/gerar_readmes.py a partir dos artefatos do dbt. Não edite à mão. -->

# 🥇 Gold

Star schema servido ao backend e ao Grafana. Só agregados cruzam a fronteira (LGPD).

## `gold.dim_data` · table

Dimensão calendário, um registro por dia no intervalo de sintomas observado.

| Coluna | Tipo | Descrição |
|---|---|---|
| `data` | date | Data (PK). |
| `ano` | integer | Ano (inteiro). |
| `mes` | integer | Mês do ano (1-12). |
| `ano_mes` | text | Competência mensal (YYYY-MM), usada na série de 12 meses. |
| `dia` | integer | Dia do mês (1-31). |
| `dia_semana` | integer | Dia da semana ISO (1=segunda … 7=domingo). |
| `semana_iso` | integer | Número da semana ISO no ano. |

## `gold.dim_uf` · table

Dimensão de UF (sigla → nome e região), a partir do seed versionado.

| Coluna | Tipo | Descrição |
|---|---|---|
| `uf` | text | Sigla da UF (PK). 'NA' para desconhecida. |
| `uf_nome` | text | Nome por extenso da UF. |
| `regiao` | text | Região geográfica (Norte, Nordeste, Centro-Oeste, Sudeste, Sul). |

## `gold.fct_srag_diario` · table

Fato agregado de SRAG por (dia do 1º sintoma, UF). Medidas aditivas; grão único. Fonte das 4 métricas e dos 2 gráficos. Só contagens — servido, sem microdado.

| Coluna | Tipo | Descrição |
|---|---|---|
| `dt` | date | Data do 1º sintoma (FK → dim_data.data). |
| `uf` | text | UF de residência (FK → dim_uf.uf). |
| `casos` | bigint | Total de casos (notificações) no dia/UF. |
| `curas` | bigint | Casos com desfecho cura (EVOLUCAO=1). |
| `obitos` | bigint | Óbitos por SRAG (EVOLUCAO=2) — numerador da mortalidade. |
| `obitos_outras_causas` | bigint | Óbitos por outras causas (EVOLUCAO=3). |
| `casos_uti` | bigint | Casos que foram à UTI (UTI=1) — numerador do proxy de UTI. |
| `casos_uti_nao` | bigint | Casos sem UTI (UTI=2) — compõe o denominador do proxy de UTI. |
| `vacinados` | bigint | Casos vacinados p/ COVID (VACINA_COV=1) — numerador do proxy de vacinação. |
| `nao_vacinados` | bigint | Casos não vacinados (VACINA_COV=2) — compõe o denominador do proxy. |

## `gold.gold_mart_srag_diario` · view

View de serviço (contrato do backend/Grafana): fato denormalizado com dim_uf. Mantém os nomes de coluna esperados pela camada de tools (ev_*, uti_*, vac_*).

| Coluna | Tipo | Descrição |
|---|---|---|
| `dt` | date | Data do 1º sintoma. |
| `uf` | text | Sigla da UF. |
| `uf_nome` | text | Nome por extenso da UF (de dim_uf). |
| `regiao` | text | Região geográfica (de dim_uf). |
| `casos` | bigint | Total de casos no dia/UF. |
| `ev_cura` | bigint | Curas (alias de fct.curas). |
| `ev_obito` | bigint | Óbitos por SRAG (alias de fct.obitos). |
| `ev_obito_outras` | bigint | Óbitos por outras causas (alias de fct.obitos_outras_causas). |
| `uti_sim` | bigint | Casos com UTI (alias de fct.casos_uti). |
| `uti_nao` | bigint | Casos sem UTI (alias de fct.casos_uti_nao). |
| `vac_sim` | bigint | Vacinados (alias de fct.vacinados). |
| `vac_nao` | bigint | Não vacinados (alias de fct.nao_vacinados). |

---
Documentação completa (testes, lineage) no site do dbt: `dbt docs generate && dbt docs serve` (ou `docker compose --profile docs up dbt-docs`, porta 8080).
