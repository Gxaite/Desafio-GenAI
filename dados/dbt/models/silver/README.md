<!-- GERADO por scripts/gerar_readmes.py a partir dos artefatos do dbt. Não edite à mão. -->

# Silver

Casos limpos, tipados e deduplicados, com marcadores de negócio. Ainda a nível de caso, não é servido.

## `silver.silver_srag_casos` (table)

Casos de SRAG limpos, tipados e deduplicados por notificação (1 linha/caso), com flags de negócio (óbito, UTI, vacinação e "conhecido") que alimentam o fato agregado da gold. Camada silver: ainda a nível de caso, não é servida — só a gold cruza a fronteira.

| Coluna | Tipo | Descrição |
|---|---|---|
| `nu_notificacao` | text | Número da notificação — chave do caso. |
| `dt_sintomas` | date | Data dos primeiros sintomas (date). |
| `uf` | text | UF de residência (sigla; 'NA' quando ausente). |
| `evolucao` | text | Desfecho: 1=cura, 2=óbito, 3=óbito outras causas, 9=ignorado. |
| `uti` | text | Internação em UTI: 1=sim, 2=não, 9=ignorado. |
| `vacina_covid` | text | Vacinado COVID: 1=sim, 2=não, 9=ignorado. |

---
Documentação completa, com testes e lineage, no site do dbt. Rode `dbt docs generate && dbt docs serve` ou `docker compose --profile docs up dbt-docs` (porta 8080).
