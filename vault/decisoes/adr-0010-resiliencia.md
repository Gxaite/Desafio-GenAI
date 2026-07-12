---
tags: [decisao, adr, resiliencia]
status: aceito
data: 2026-07-09
revisado: 2026-07-12
---

# ADR-0010 — Estratégia de Resiliência (fail-fast, sem fallback)

- **Status:** aceito (revisado em 2026-07-12)
- **Data:** 2026-07-09

## Contexto
O agente depende de serviços externos falíveis (NewsAPI, LLM/OpenRouter). A versão inicial
adotava **degradação graciosa** (relatório saía sem notícias ou com narrativa determinística
quando o LLM falhava). Na prática, isso **mascarou uma falha real**: uma chave de LLM inválida
(HTTP 401) passou despercebida e o relatório saiu com narrativa determinística que ainda
dizia, no rodapé, "narrativa escrita pelo LLM". Para uma solução de saúde, um relatório
silenciosamente degradado é pior do que nenhum relatório.

## Decisão
**Fail-fast, sem fallback.** Nos adapters, manter **timeouts** explícitos e **retry com backoff
exponencial + jitter** (`tenacity`) apenas para erros transitórios (rede, 429, 5xx). Esgotados
os retries, ou em erro permanente (401, chave ausente), a falha vira um `SragReportError`
tipado e **sobe**: a execução falha explicitamente e a API responde **503** (ou emite um
evento `erro` no stream). Não há narrativa determinística nem relatório sem notícias — se um
insumo obrigatório falta, não se entrega um relatório que aparente estar completo.
Detalhes em [[qualidade-governanca]].

## Alternativas consideradas
- **Degradação graciosa (decisão anterior)** — entrega sempre, mas pode mascarar falha e
  enganar o usuário sobre a origem do conteúdo. Rejeitada por esse risco.
- Retry infinito sem limite — risco de martelar serviço caído. Rejeitada.

## Consequências
- Confiabilidade: o que sai do sistema é sempre íntegro; falha é visível, não silenciosa.
- Disponibilidade menor: uma queda de NewsAPI/OpenRouter derruba a geração do relatório
  (aceitável para uma PoC, onde correção > cobertura).
- Toda falha é auditada na trilha por `run_id` ([[qualidade-governanca]]).

## Relacionadas
[[qualidade-governanca]] · [[adr-0001-provedor-llm]]
