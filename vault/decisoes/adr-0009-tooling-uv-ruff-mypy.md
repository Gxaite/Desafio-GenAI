---
tags: [decisao, adr, tooling]
status: aceito
data: 2026-07-09
---

# ADR-0009 — Tooling: uv + ruff + mypy + pre-commit + CI

- **Status:** aceito
- **Data:** 2026-07-09

## Contexto
*Clean Code* é critério avaliado. Um projeto-referência precisa
de portões de qualidade automatizados e reprodutíveis.

## Decisão
Padronizar o stack moderno de qualidade: **uv** (pacotes/venv), **ruff** (lint+format),
**mypy --strict** (tipos), **pytest** (testes), **import-linter** (fronteiras),
**pre-commit** e **GitHub Actions** (CI). Detalhes em [[qualidade-governanca]].

## Alternativas consideradas
- poetry + black + isort + flake8 — mais peças; ruff/uv consolidam e são mais rápidos.
- Sem CI/hooks — inaceitável para projeto-referência.

## Consequências
- Ambiente reprodutível (`uv.lock`) e feedback rápido.
- Qualidade verificada a cada commit/push.

## Relacionadas
[[qualidade-governanca]] · [[arquitetura]] · [[arquitetura]]
