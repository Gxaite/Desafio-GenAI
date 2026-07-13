# 🥉 Bronze — landing bruto

Camada de entrada do medallion. Guarda os dados de origem **como chegaram**, sem transformação.

| Objeto (schema) | O que é | Materialização |
|---|---|---|
| `bronze.srag_raw` | Registros de SRAG (SIVEP-Gripe) 2025+2026 como texto. Apenas as **~6 colunas** necessárias às métricas (minimização LGPD), mais `arquivo_origem` para proveniência. | Carregado pelo EL (Python, `COPY`) |

- **Declaração:** `_bronze__sources.yml` (dbt *source*; descrições e teste `not_null`).
- **Carga:** `dados/src/srag_etl/extract_load.py` — baixa o CSV do Open DATASUS (se não houver local) e faz `COPY` para o Postgres. Proveniência registrada em `bronze.etl_run`.
- **Próxima camada:** [../silver](../silver).

Documentação completa (colunas e testes) nos arquivos `.yml` desta pasta e no site navegável
via `dbt docs generate && dbt docs serve`. Visão geral do ETL em
[`../../../../vault/camada-dados.md`](../../../../vault/camada-dados.md).
