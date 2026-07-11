---
tags: [arquitetura, privacidade, lgpd]
atualizado: 2026-07-09
---

# Tratamento de Dados Sensíveis

Os microdados do [[srag-datasus]] contêm **dados pessoais sensíveis de saúde** (LGPD,
art. 5º, II). Critério próprio em [[criterios-avaliacao]].

## Princípios adotados

- **Minimização** — carregar apenas colunas necessárias às [[metricas]].
- **Só agregados cruzam a fronteira** — nenhum dado a nível de indivíduo sai da
  [[camada-dados]]; tools e relatório operam sobre contagens/taxas.
- **Sem identificadores diretos** — descartar/nunca expor campos como município de
  residência combinado com idade/sexo/raça (risco de reidentificação).
- **Segredos fora do código** — chaves (OpenRouter, NewsAPI) via `.env` ([[stack]]).
- **Rastreabilidade** — decisões de anonimização registradas ([[governanca-auditoria]]).

## Guardrail associado
O agente é impedido de emitir qualquer recorte que permita reidentificação ([[guardrails]]).
