---
tags: [arquitetura, relatorio]
atualizado: 2026-07-09
---

# Geração de Relatório

Monta o entregável final a partir do estado produzido pelo [[agente-orquestrador]].

## Conteúdo

- As 4 [[metricas]] com valores, período e N.
- **2 gráficos** (matplotlib → PNG): casos diários (30d) e mensais (12m).
- **Narrativa** do LLM: contextualiza as métricas com as notícias ([[camada-tools]]).
- Nota de premissas (proxies de UTI/vacinação — [[adr-0007-metricas-proxy]]).
- Rodapé de transparência: modelo usado, fontes, timestamp ([[qualidade-governanca]]).

## Pipeline

`Markdown (template)` → `HTML` → **WeasyPrint** → `PDF`.

## Entregáveis relacionados

- Relatório em PDF (saída do agente).
- **Diagrama conceitual** da arquitetura em PDF (deriva de [[arquitetura]]).
- README do repositório, alimentado por este vault.
