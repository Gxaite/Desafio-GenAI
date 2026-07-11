---
tags: [arquitetura, guardrails]
atualizado: 2026-07-09
---

# Guardrails

Mecanismos que impedem o sistema de produzir resultados incorretos, inventados ou
inseguros. Critério próprio em [[criterios-avaliacao]].

## Camadas de proteção

1. **Entrada** — validação de parâmetros via pydantic ([[camada-tools]]).
2. **Grounding obrigatório** — o LLM só narra sobre números vindos das tools; **nunca
   calcula nem inventa métricas** ([[adr-0004-llm-orquestra-python-calcula]]).
3. **Relevância de notícias** — filtro de tema (SRAG/saúde) antes de usar ([[camada-tools]]).
4. **Saída** — validar que toda métrica citada na narrativa existe no estado; sinalizar
   divergências ([[agente-orquestrador]]).
5. **Dados sensíveis** — bloquear qualquer vazamento a nível de indivíduo ([[dados-sensiveis]]).
6. **Falha explícita** — na ausência de dado, retornar erro/《N/A》 em vez de improvisar.

## Relação
Guardrails + [[governanca-auditoria]] andam juntos: o que a auditoria registra, os
guardrails previnem.
