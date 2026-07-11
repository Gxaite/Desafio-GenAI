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

## Camadas medallion

| Camada | Objeto | O que é | Motor |
|---|---|---|---|
| 🥉 **bronze** | `bronze.srag_raw` | landing bruto (texto), 1 linha/registro + arquivo de origem. Só as **~6 colunas** necessárias às [[metricas]] (minimização) | EL (Python, `COPY`) |
| 🥈 **silver** | `silver.srag_casos` | limpo, tipado (data ISO→`date`) e **deduplicado** por `NU_NOTIFIC`; 1 linha/caso | dbt |
| 🥇 **gold** | `gold.mart_srag_diario` | **agregado** por (dia, UF): `casos` + contagens de `EVOLUCAO`/`UTI`/`VACINA_COV`. Único servido | dbt |

As 4 [[metricas]] e os 2 gráficos derivam do **gold** por SQL (denominadores usam só
valores conhecidos: 1/2). Testes `dbt` (`not_null`, `unique`, `accepted_values`, grão
único) validam cada camada.

## Princípios
- ETL **determinístico e idempotente** — `TRUNCATE`+recarrega bronze; dbt reconstrói
  silver/gold ([[qualidade-governanca]]).
- Proveniência registrada em `bronze.etl_run` (linhas lidas, arquivos, timestamp).
- **Só a gold cruza a fronteira** para consumo; nenhum agregado expõe indivíduo. O bruto
  minimizado transita por bronze/silver (trade-off documentado em [[adr-0015-dbt-medallion]]).

Consumida por → [[camada-tools]] (backend) e [[arquitetura]] (Grafana).
