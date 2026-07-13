# 🥇 Gold — star schema servido

Modelagem dimensional consumida pelo backend (relatório) e pelo Grafana. **Só agregados** cruzam
a fronteira — nenhum dado a nível de indivíduo sai daqui (LGPD).

| Objeto (schema) | O que é | Materialização |
|---|---|---|
| `gold.dim_uf` | Dimensão de UF (sigla → nome e região), a partir do seed versionado. | table |
| `gold.dim_data` | Dimensão calendário, um registro por dia do intervalo observado. | table |
| `gold.fct_srag_diario` | **Fato** de grão (dia do 1º sintoma, UF): medidas aditivas + FKs para as dimensões. Fonte das 4 métricas e dos 2 gráficos. | table |
| `gold.gold_mart_srag_diario` | **View de serviço** (contrato estável do backend/Grafana): fato denormalizado com `dim_uf`, mantendo os nomes de coluna esperados pelas tools. | view |

- **Origem:** [../silver](../silver) (`silver.silver_srag_casos`).
- **Qualidade (dbt tests):** `relationships` (fato → dims), grão único, coerência de medidas,
  `not_null`, `unique`, `accepted_values` — ver `_gold__models.yml` e `../../tests/`.
- **Lineage:** `_exposures.yml` declara o consumo até o **relatório PDF** e o **dashboard Grafana**.

Star schema minimizado a `dim_uf` + `dim_data` por LGPD (sem dimensões demográficas de indivíduo).
Decisão em [`../../../../vault/decisoes/adr-0016-modelagem-dimensional.md`](../../../../vault/decisoes/adr-0016-modelagem-dimensional.md).
