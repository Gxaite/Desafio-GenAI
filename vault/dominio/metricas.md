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

> Nota. Ocupação de UTI e vacinação são calculadas sobre as pessoas avaliadas (status por
> caso), não sobre o total de leitos nem a população. A premissa é documentada no relatório
> (rigor valorizado nos critérios de avaliação).

## Dados provisórios (atraso de notificação)

Os dias mais recentes da base são **subnotificados** (as notificações chegam com atraso), então a
cauda da série cai artificialmente. Para não apresentar queda falsa, a referência recua
`DADOS_DIAS_PROVISORIOS` dias (default 14) e as métricas/gráficos terminam no último dia
confiável. Decisão e efeito (-35% falso → -0,48% real) em [[adr-0017-dados-provisorios]].

## Os 2 gráficos exigidos

1. **Casos diários** — últimos 30 dias.
2. **Casos mensais** — últimos 12 meses.

Renderizados em Plotly na [[geracao-relatorio]], a partir da tool `dados_grafico`.
