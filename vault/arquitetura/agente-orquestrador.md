---
tags: [arquitetura, agente]
atualizado: 2026-07-09
---

# Agente Orquestrador (LangGraph)

O cérebro de execução. Implementado como um **grafo de estados** ([[adr-0005-langgraph]]),
o que torna cada decisão um nó explícito e logável ([[governanca-auditoria]]).

## Estado (rascunho)

```python
class EstadoRelatorio(TypedDict):
    periodo: str
    metricas: dict | None
    series: dict | None
    noticias: list | None
    narrativa: str | None
    trilha: list          # eventos de auditoria
```

## Nós (MVP linear)

1. `no_metricas` → chama `calcular_metricas`
2. `no_graficos` → chama `dados_grafico`
3. `no_noticias` → chama `buscar_noticias`
4. `no_narrativa` → LLM contextualiza métricas com base nas notícias
5. `no_relatorio` → dispara [[geracao-relatorio]]

## Evolução para PoC completa

- Arestas **condicionais**: se uma métrica vier vazia, decidir re-consultar ou sinalizar.
- Validação entre nós (grounding) — [[guardrails]].
- Seleção de modelo por nó ([[adr-0001-provedor-llm]]): Haiku p/ orquestrar, Sonnet p/ narrar.
