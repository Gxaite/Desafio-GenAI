# Modelos dbt (medallion bronze, silver, gold)

Uma pasta por camada, editável isoladamente. Cada camada tem seu próprio README, gerado a
partir dos artefatos do dbt.

| Camada | Pasta | O que é |
|---|---|---|
| Bronze | [`bronze/`](bronze) | Landing bruto (source `srag_raw`), carregado pelo EL em Python. |
| Silver | [`silver/`](silver) | `silver_srag_casos`, com limpeza, tipagem, deduplicação e marcadores de negócio. |
| Gold | [`gold/`](gold) | Star schema servido (dimensões, fato e view de serviço). |

Fluxo dos dados. CSV do Open DATASUS vira bronze, depois silver, depois gold, e a gold alimenta
o relatório em PDF e o Grafana.

O mapeamento das camadas para os schemas do Postgres fica em
[`../dbt_project.yml`](../dbt_project.yml). A documentação completa, com descrições de tabelas e
colunas e os testes, está nos arquivos `.yml` de cada pasta e no site navegável do dbt (rode
`dbt docs generate && dbt docs serve`, ou `docker compose --profile docs up dbt-docs`, na porta
8080). O dicionário de dados do projeto está em
[`../../../docs/dicionario-de-dados.md`](../../../docs/dicionario-de-dados.md) e a visão geral do
ETL em [`../../../vault/camada-dados.md`](../../../vault/camada-dados.md).
