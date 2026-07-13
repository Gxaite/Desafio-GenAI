# 🥈 Silver — limpo, tipado e deduplicado

Transforma o bronze em casos prontos para agregação. Ainda a nível de caso, **não é servido**
ao backend nem ao Grafana (só a gold cruza a fronteira).

| Objeto (schema) | O que é | Materialização |
|---|---|---|
| `silver.silver_srag_casos` | Tipa datas (ISO → `date`), normaliza vazios, **deduplica** por notificação (1 linha por caso) e deriva as **flags de negócio** (`is_obito`, `foi_uti`, `vacinado`, `*_conhecido`) usadas pelas métricas. | table |

- **Origem:** [../bronze](../bronze) (`bronze.srag_raw`).
- **Consumida por:** [../gold](../gold) (fato e dimensões).
- **Docs e testes:** `_silver__models.yml` — `not_null`, `unique` (notificação) e `accepted_values`
  nos campos categóricos (`evolucao`, `uti`, `vacina_covid`).

Denominadores das taxas usam só valores conhecidos (1/2); ignorados e ausentes ficam de fora.
Site navegável via `dbt docs`. Visão geral em
[`../../../../vault/camada-dados.md`](../../../../vault/camada-dados.md).
