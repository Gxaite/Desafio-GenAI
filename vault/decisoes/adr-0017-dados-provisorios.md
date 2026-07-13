---
tags: [decisao, adr, dados, metricas]
status: aceito
data: 2026-07-13
---

# ADR-0017 — Excluir dias provisórios (atraso de notificação)

- **Status:** aceito
- **Data:** 2026-07-13

## Contexto
A base de SRAG (SIVEP-Gripe) tem **atraso de notificação**: casos com `DT_SIN_PRI` recente ainda
não receberam todas as notificações, então a cauda da série diária despenca artificialmente. No
snapshot usado (dados até 2026-07-05), os últimos ~10 dias caem de ~1.200 para **3** casos/dia —
não porque o surto acabou, mas porque o dado ainda está incompleto.

Com a referência ancorada em `max(dt)`, a janela "últimos 30 dias" incluía essa cauda, e a **taxa
de aumento de casos** comparava um período subnotificado contra um completo, produzindo uma queda
**falsa de -35%**. Métricas e gráficos apresentavam dado que não existe.

## Decisão
Tratar os **últimos N dias como provisórios** e recuar a referência de análise em N dias a partir
do último dia com dado. Todas as métricas e os dois gráficos passam a terminar no **último dia
confiável**, sem a cauda subnotificada.

- `N` é configurável via `DADOS_DIAS_PROVISORIOS` (default **14** — duas semanas, prática comum em
  vigilância epidemiológica). `0` desativa (usa `max(dt)`).
- Ponto único: `referencia_efetiva()` em `application/tools.py`; injetado no grafo e nos endpoints.
- Efeito medido: taxa de aumento passou de **-35,09%** (falsa) para **-0,48%** (janelas completas).

## Alternativas consideradas
- **Manter `max(dt)`** — simples, mas apresenta queda falsa; descartado (engana o leitor).
- **Só marcar a cauda como provisória** (sombrear no gráfico, sem excluir) — honesto, mas ainda
  mostra a queda e exige lógica de UI; preferimos excluir e documentar.
- **Detectar o corte automaticamente** (último dia "estável") — exigiria múltiplos snapshots para
  medir o atraso; frágil com um único arquivo.

## Consequências
- Números de destaque passam a ser confiáveis; o "mais recente" fica ~2 semanas defasado (aceitável
  e explicado no rodapé do relatório e no [[dicionario-de-dados]]).
- Decisão configurável (12-factor) — ambientes com dado mais/menos atrasado ajustam `N`.
- O Grafana, que lê a gold direto, aplica o mesmo corte nas queries dos painéis diários/semanais.

## Relacionadas
[[metricas]] · [[camada-dados]] · [[adr-0007-metricas-proxy]] · [[srag-datasus]]
