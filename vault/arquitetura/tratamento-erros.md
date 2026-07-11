---
tags: [arquitetura, erros]
atualizado: 2026-07-09
---

# Tratamento de Erros

Erros são **explícitos e tipados**. Fronteiras convertem falhas de infraestrutura em
erros de domínio compreensíveis. Sustenta [[resiliencia]] e [[principios]] (fail-fast).

## Hierarquia (em `domain/errors.py`)

```
SragReportError                 # base
├── ErroDados                   # ETL/repositório: dado ausente, coluna inválida
├── ErroFonteNoticias           # NewsAPI indisponível/limite
├── ErroModeloLLM               # falha do LLM/OpenRouter
├── ErroGuardrail               # violação de validação/grounding
└── ErroConfiguracao            # config/segredo ausente (fail-fast no boot)
```

## Regras
- **Fronteira traduz**: adapters capturam exceções de SDK e relançam como erro de
  domínio ([[estrutura-projeto]]) — o domínio nunca vê `requests.HTTPError`.
- **Transitório vs permanente**: transitório → retry ([[resiliencia]]); permanente → falha clara.
- **Sem `except:` nu**; sem engolir exceção. Todo erro tratado é logado ([[observabilidade]]).
- **Config inválida falha no boot**, não em runtime ([[principios]], 12-factor).
- Guardrails levantam `ErroGuardrail` em vez de deixar passar dado inventado ([[guardrails]]).

## Ligações
[[resiliencia]] · [[guardrails]] · [[observabilidade]]
