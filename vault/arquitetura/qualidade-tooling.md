---
tags: [arquitetura, qualidade, tooling]
atualizado: 2026-07-09
---

# Qualidade e Tooling

Portões automatizados que fazem o projeto ser **referência** e sustentam o critério
*Clean Code* ([[criterios-avaliacao]]). Decisão em [[adr-0009-tooling-uv-ruff-mypy]].

## Ferramentas

| Área | Ferramenta | Papel |
|---|---|---|
| Gerência de pacote/venv | **uv** | rápido, lockfile determinístico, PEP 621 |
| Lint + format | **ruff** | um só tool, substitui flake8/black/isort |
| Tipagem estática | **mypy --strict** | type safety de ponta a ponta |
| Testes | **pytest** + `pytest-cov` | unit (domínio) + integração (adapters) |
| Fronteiras de import | **import-linter** | impõe regras de dependência do hexágono ([[estrutura-projeto]]) |
| Hooks | **pre-commit** | roda ruff/mypy antes do commit |
| CI | **GitHub Actions** | lint + type + test em cada push |
| Tarefas | **justfile** | `just test`, `just run`, `just lint` |

## Estratégia de testes
- **Domínio** ([[metricas]]): funções puras → testes sem mocks, casos de dados sujos.
- **Adapters**: testes de integração com fakes/gravações; sem chamar APIs reais no CI.
- **Guardrails**: testes provando que dado inventado é bloqueado ([[guardrails]]).

## Convenções
- Docstrings + type hints obrigatórios em APIs públicas.
- Commits convencionais (`feat:`, `fix:`, `docs:`).
- Cobertura mínima no núcleo de domínio.

## Ligações
[[estrutura-projeto]] · [[principios]] · [[stack]]
