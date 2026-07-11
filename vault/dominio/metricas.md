---
tags: [dominio, metricas]
atualizado: 2026-07-09
---

# Métricas e Gráficos

As 4 métricas exigidas são **sempre calculadas em SQL/Python determinístico**
(nunca pelo LLM — ver [[adr-0004-llm-orquestra-python-calcula]]) e expostas via
[[camada-tools]].

## As 4 métricas

| Métrica | Definição adotada | Fonte |
|---|---|---|
| **Taxa de aumento de casos** | variação % de casos entre períodos (ex.: semana atual vs. anterior) | `DT_SIN_PRI` |
| **Taxa de mortalidade** | óbitos / total de casos (`EVOLUCAO == 2`) | `EVOLUCAO` |
| **Taxa de ocupação de UTI** | *proxy*: casos com `UTI == 1` / internações | `UTI` → [[adr-0007-metricas-proxy]] |
| **Taxa de vacinação** | *proxy*: % de casos vacinados (`VACINA_COV`) | `VACINA_COV` → [[adr-0007-metricas-proxy]] |

> ⚠️ Ocupação de UTI e vacinação são **proxies** — a base traz status por caso, não
> leitos totais nem cobertura populacional. A premissa é documentada no relatório
> (rigor premiado em critérios de avaliação).

## Os 2 gráficos exigidos

1. **Casos diários** — últimos 30 dias.
2. **Casos mensais** — últimos 12 meses.

Renderizados em Plotly na [[geracao-relatorio]], a partir da tool `dados_grafico`.
