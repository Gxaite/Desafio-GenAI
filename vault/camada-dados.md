---
tags: [arquitetura, dados]
atualizado: 2026-07-09
---

# Camada de Dados (ETL medallion → Postgres)

Serviço `dados` ([[arquitetura]]): transforma o CSV bruto do [[srag-datasus]] numa
**arquitetura medallion** (bronze → silver → gold) e serve o mart agregado no Postgres.
Motor: **EL em Python + dbt** ([[adr-0015-dbt-medallion]]).

## Achados reais dos arquivos (validados na sondagem)
- Delimitador **`;`**, campos entre **aspas**, **194 colunas**, datas em **ISO 8601**
  (`2025-06-12T00:00:00.000Z`), encoding **UTF-8**.
- `srag-2025`: 336.265 linhas; `srag-2026`: 154.841 linhas. `NU_NOTIFIC` é **único por
  arquivo** (sem nulos) e os conjuntos são **disjuntos** entre os dois → **não há duplicação
  cruzada**; basta **unir** (dedup por `NU_NOTIFIC` fica só como salvaguarda).
- Os ~1.649 registros do arquivo de 2025 com `DT_SIN_PRI` em 2026 são **casos distintos**
  (sintoma na virada de ano), não duplicatas. As séries agregam por `DT_SIN_PRI`, então cada
  caso conta uma vez.

## Medallion + layering idiomático dbt

Medallion mapeado ao layering dbt (**staging → intermediate → marts**) e **modelagem
dimensional** (star schema) na gold ([[adr-0016-modelagem-dimensional]]):

| Camada | Objeto (schema) | O que é | Materialização |
|---|---|---|---|
| 🥉 **bronze** | `bronze.srag_raw` | landing bruto (texto) + `arquivo_origem`. Só as **~6 colunas** necessárias (minimização LGPD) | EL Python (`COPY`) |
| 🥈 **silver / staging** | `silver.stg_srag__casos` | 1:1 da fonte: renomeia, tipa (data ISO→`date`), normaliza vazios | view |
| 🥈 **silver / intermediate** | `silver.int_srag__casos` | **dedup** por notificação + flags de negócio (`is_obito`, `foi_uti`, `vacinado`, `*_conhecido`) | table |
| 🥇 **gold / dims** | `gold.dim_uf`, `gold.dim_data` | dimensões: UF (via **seed** → nome/região) e calendário | table |
| 🥇 **gold / fato** | `gold.fct_srag_diario` | **fato** grão (dia, UF): medidas aditivas; FKs p/ dims | table |
| 🥇 **gold / serviço** | `gold.gold_mart_srag_diario` | **view de serviço** (contrato do backend/Grafana): fato + `dim_uf` (nome/região) | view |

As 4 [[metricas]] e os 2 gráficos derivam do **fato** (via view de serviço). Denominadores
usam só valores conhecidos (1/2).

**Qualidade de dados (dbt tests):** `not_null`, `unique`, `accepted_values`, **relationships**
(fato → dimensões), grão único e coerência de medidas (não-negativas, sub-contagens ≤ total).
**Lineage** declarado até o relatório e o Grafana via `exposures`. Docs persistidos como
comentários no Postgres (`persist_docs`).

## Princípios
- ETL **determinístico e idempotente** — `TRUNCATE`+recarrega bronze; `dbt build` reconstrói
  seed + staging + intermediate + marts + testes ([[qualidade-governanca]]).
- Proveniência registrada em `bronze.etl_run` (linhas lidas, arquivos, timestamp).
- **Só a gold cruza a fronteira** para consumo; nenhum agregado expõe indivíduo. O bruto
  minimizado transita por bronze/silver (trade-off em [[adr-0015-dbt-medallion]]).

Consumida por → [[camada-tools]] (backend) e [[arquitetura]] (Grafana).
