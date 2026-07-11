---
tags: [arquitetura, visualizacao, grafana]
atualizado: 2026-07-09
---

# Visualização / BI (Grafana)

Camada **interativa** de dashboards, lendo o Postgres ([[adr-0006-duckdb]]). Decisão em
[[adr-0014-grafana]]. É **bônus**, não substitui o relatório PDF ([[geracao-relatorio]]).

## Escopo
- Painéis das [[metricas]]: taxa de aumento, mortalidade, ocupação de UTI (proxy),
  vacinação (proxy — [[adr-0007-metricas-proxy]]).
- Séries temporais: **casos diários (30d)** e **casos mensais (12m)** — o forte do Grafana.
- Filtros por período/UF (respeitando [[dados-sensiveis]]: só agregados).

## Provisioning como código
- `grafana/provisioning/datasources/` → conexão Postgres parametrizada via `.env`.
- `grafana/provisioning/dashboards/` → dashboards em JSON versionados.
- Nada de configuração manual perdida: reprodutível ([[adr-0013-containerizacao]]) e
  auditável ([[governanca-auditoria]]).

## Fronteira clara
| Necessidade | Solução |
|---|---|
| 2 gráficos **obrigatórios** no relatório | matplotlib no PDF ([[geracao-relatorio]]) |
| Dashboard **interativo** | Grafana (esta nota) |
| Diagrama **conceitual da arquitetura** | Mermaid/draw.io → PDF ([[visao-geral]]) |

## Ligações
[[adr-0014-grafana]] · [[containerizacao]] · [[metricas]] · [[geracao-relatorio]]
