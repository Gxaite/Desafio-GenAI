---
tags: [arquitetura, resiliencia]
atualizado: 2026-07-09
---

# Resiliência

Toda borda externa (NewsAPI, LLM/OpenRouter, disco) pode falhar. O sistema **degrada
com elegância** em vez de quebrar. Decisão em [[adr-0010-resiliencia]].

## Padrões aplicados (nos adapters — [[estrutura-projeto]])

| Padrão | Onde | Como |
|---|---|---|
| **Timeout** | todo I/O externo | limite explícito por chamada; nunca esperar infinito |
| **Retry + backoff exponencial com jitter** | NewsAPI, LLM | `tenacity`; só em erros transitórios (5xx, timeout, rate-limit) |
| **Circuit breaker** | NewsAPI, LLM | abre após N falhas; evita martelar serviço caído |
| **Degradação graciosa** | orquestração | relatório sai **mesmo sem notícias**, sinalizando a ausência |
| **Idempotência** | ETL | mesma entrada → mesma saída; reprocessar é seguro ([[camada-dados]]) |
| **Bulkhead / limites** | LLM/notícias | isolar falhas de um recurso para não derrubar o pipeline |
| **Fallback de modelo** | LLM | se o modelo primário falhar, cair para alternativa ([[adr-0001-provedor-llm]]) |

## Princípios
- Distinguir **erro transitório** (retry) de **erro permanente** (falha rápida) — ver [[tratamento-erros]].
- Toda falha/fallback é **registrada** na trilha ([[observabilidade]], [[governanca-auditoria]]).
- Resiliência é responsabilidade da **infraestrutura**; o domínio permanece puro ([[principios]]).

## Ligações
[[tratamento-erros]] · [[observabilidade]] · [[agente-orquestrador]]
