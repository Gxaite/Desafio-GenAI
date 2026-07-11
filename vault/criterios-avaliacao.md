---
tags: [planejamento, avaliacao]
atualizado: 2026-07-09
---

# Critérios de Avaliação

Estes são os critérios do desafio. Cada um é atacado por uma parte da arquitetura —
por isso servem de guia para onde investir esforço.

| Critério | Onde é atendido |
|---|---|
| **Escolha da arquitetura** | [[visao-geral]], [[adr-0005-langgraph]], [[adr-0004-llm-orquestra-python-calcula]] |
| **Governança e Transparência** | [[governanca-auditoria]] — log estruturado de decisões e tool calls |
| **Guardrails** | [[guardrails]] — validação I/O, *grounding*, recusa de fabricar números |
| **Uso de Tools** | [[camada-tools]] — 3 tools com schemas tipados |
| **Tratamento de Dados Sensíveis** | [[dados-sensiveis]] — só agregados, LGPD |
| **Clean Code** | [[stack]] — módulos, tipagem, config externa, testes |

## Entregáveis exigidos

- Explicações/documentação no **README** do repositório (este vault alimenta isso).
- **PDF com diagrama conceitual** da arquitetura (Orquestrador + Tools + LLM + BD + notícias) — ver [[visao-geral]].
- Relatório gerado com as [[metricas]] + 2 gráficos.
- "Entregue o que conseguir" → reforça a [[adr-0003-estrategia-mvp-primeiro]].
