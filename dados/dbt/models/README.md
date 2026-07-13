# Modelos dbt — medallion (bronze → silver → gold)

Uma **pasta por camada**, editável isoladamente. Cada camada tem seu próprio `README.md`.

| Camada | Pasta | O que é |
|---|---|---|
| 🥉 Bronze | [`bronze/`](bronze) | Landing bruto (source `srag_raw`), carregado pelo EL em Python. |
| 🥈 Silver | [`silver/`](silver) | `silver_srag_casos`: limpeza, tipagem, dedup e flags de negócio. |
| 🥇 Gold | [`gold/`](gold) | Star schema servido (dimensões + fato + view de serviço). |

Fluxo: `CSV (Open DATASUS) → bronze → silver → gold → relatório PDF / Grafana`.

- **Mapeamento medallion → dbt/schemas:** definido em [`../dbt_project.yml`](../dbt_project.yml)
  (`silver` e `gold` como schemas no Postgres).
- **Documentação completa** (descrições de tabelas/colunas e testes): nos arquivos `.yml` de cada
  pasta e no site navegável do dbt: `dbt docs generate && dbt docs serve` (http://localhost:8080).
- **Dicionário de dados** do projeto: [`../../../docs/dicionario-de-dados.md`](../../../docs/dicionario-de-dados.md).
- **Visão geral do ETL:** [`../../../vault/camada-dados.md`](../../../vault/camada-dados.md).
