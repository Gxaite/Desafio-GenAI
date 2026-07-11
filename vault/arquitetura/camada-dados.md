---
tags: [arquitetura, dados]
atualizado: 2026-07-09
---

# Camada de Dados (ETL → Postgres)

Serviço `dados` ([[containerizacao]]): transforma o CSV bruto do [[srag-datasus]] e
**carrega os marts agregados no Postgres** ([[adr-0006-duckdb]]).

## Achados reais dos arquivos (validados)
- Delimitador **`;`**, campos entre **aspas**, **194 colunas**, datas em **ISO 8601**
  (`2025-06-12T00:00:00.000Z`), encoding provável **latin-1**.
- `srag-2025`: ~336k linhas (majoritariamente 2025); `srag-2026`: ~155k (100% 2026).
- **Sobreposição de virada de ano**: ~1.649 casos de 2026 aparecem no arquivo de 2025 →
  **deduplicar por identificador** ao unir.

## Etapas (DuckDB/pandas em memória)
1. **Extract** — ler os 2 CSVs (`;`, latin-1).
2. **Seleção de colunas** — manter só as pertinentes às [[metricas]] (de 194 p/ ~15).
3. **Clean** — datas ISO → date; normalizar `EVOLUCAO`, `UTI`, `VACINA_COV`; tratar ausentes.
4. **Dedupe** — unir 2025+2026 sem duplicar casos de virada de ano.
5. **Anonimização** — remover identificadores; só o necessário ([[dados-sensiveis]]).
6. **Agregação** — marts por dia, mês e recorte.
7. **Load** — gravar os marts no **Postgres** (tabelas servidas ao backend e ao Grafana).

## Princípios
- ETL **determinístico e idempotente** — reprocessar é seguro ([[resiliencia]]).
- Registrar contagens antes/depois da limpeza ([[governanca-auditoria]]).
- Nada a nível de indivíduo cruza a fronteira; só agregados vão ao Postgres.

Consumida por → [[camada-tools]] (backend) e [[visualizacao-bi]] (Grafana).
