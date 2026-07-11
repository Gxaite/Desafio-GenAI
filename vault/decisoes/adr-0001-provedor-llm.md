---
tags: [decisao, adr, llm]
status: aceito
data: 2026-07-09
---

# ADR-0001 — Provedor de LLM: Claude via OpenRouter

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
O desafio é agnóstico de provedor. Precisamos de um LLM para orquestração e narrativa,
com baixo atrito de setup e flexibilidade de custo.

## Decisão
Usar **modelos Claude (Anthropic) através do OpenRouter**. No LangChain, via
`ChatOpenAI` apontando para o `base_url` do OpenRouter (API compatível com OpenAI).

## Alternativas consideradas
- OpenAI/GPT direto — descartado pela preferência por Claude.
- Anthropic API direta — viável, mas OpenRouter facilita trocar de modelo e centraliza billing.
- Gemini / Ollama local — descartados para esta PoC.

## Consequências
- Troca de modelo é apenas config (uma string). Ver [[arquitetura]].
- **Haiku 4.5** para orquestrar, **Sonnet 5** para narrar ([[agente-orquestrador]]).
- Chave do OpenRouter fica no `.env` ([[qualidade-governanca]]).
- Slugs exatos do OpenRouter a confirmar ao codar.

## Relacionadas
[[adr-0005-langgraph]] · [[arquitetura]] · [[arquitetura]]
