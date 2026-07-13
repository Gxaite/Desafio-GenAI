<!-- GERADO por scripts/gerar_readmes.py a partir dos artefatos do dbt. Não edite à mão. -->

# 🥉 Bronze

Landing bruto, carregado pelo passo EL (Python). Só as colunas necessárias (minimização LGPD).

## `bronze.srag_raw` · source (via EL)

Registros de SRAG (SIVEP-Gripe) 2025+2026, como texto.

| Coluna | Tipo | Descrição |
|---|---|---|
| `nu_notific` | text | Número da notificação (identificador do registro na origem). |
| `dt_sin_pri` | text | Data dos primeiros sintomas (ISO 8601, texto). |
| `arquivo_origem` | text | Nome do CSV de origem (proveniência/lineage). |

---
Documentação completa (testes, lineage) no site do dbt: `dbt docs generate && dbt docs serve` (ou `docker compose --profile docs up dbt-docs`, porta 8080).
