---
tags: [arquitetura, tools]
atualizado: 2026-07-09
---

# Camada de Tools

Interface entre o [[agente-orquestrador]] e o mundo determinístico. Cada tool tem
**schema tipado (pydantic)** — entrada e saída validadas ([[qualidade-governanca]]).

As tools vivem em `application/tools.py` e compõem *ports* + domínio puro — não conhecem SDKs.

## Especificação técnica

### `calcular_metricas(repo, referencia=None) -> list[Metrica]`
- **O que faz:** resolve a data de referência (último dado, se `None`), agrega o período atual
  (30 dias) e o anterior via `RepositorioDados.agregado`, e aplica as funções puras de
  `domain/metrics.py`. Devolve as 4 [[metricas]] como `Metrica(nome, valor, unidade,
  denominador, observacao)`.
- **Decisão:** o cálculo é 100% determinístico (SQL + Python); o LLM nunca calcula
  ([[adr-0004-llm-orquestra-python-calcula]]). Denominadores usam só valores conhecidos (1/2)
  e a premissa vira `observacao` — transparência sem inflar/deflar a taxa.

### `dados_grafico(repo, referencia=None) -> SeriesGraficos`
- **O que faz:** monta as duas séries exigidas — `diaria_30d` e `mensal_12m` (lista de
  `PontoSerie(competencia, casos)`), via `serie_diaria`/`serie_mensal` do repositório.
- **Decisão:** a tool devolve **dados**, não imagem — a renderização (Plotly) fica na
  [[geracao-relatorio]]. Separar dado de apresentação permite reusar as séries no PDF, na API
  e em testes sem acoplar a biblioteca de gráficos.

### `buscar_noticias(fonte, consulta="SRAG", *, limite=5) -> list[Noticia]`
- **O que faz:** chama `FonteNoticias.buscar` (adapter NewsAPI — [[adr-0002-fonte-noticias]])
  e aplica `domain/news.filtrar_relevantes` (guardrail) antes de devolver `Noticia(titulo,
  fonte, url, publicado_em, descricao)`.
- **Decisão:** o **filtro de relevância** é função pura e testável, separada do I/O; sem chave
  ou em falha transitória, o adapter degrada para `[]` (o relatório sai mesmo sem notícias —
  [[qualidade-governanca]]).

## Princípios
- Tools **não alucinam**: retornam dado de fonte (validado por schema pydantic) ou erro tipado.
- Cada chamada vira um evento na trilha de auditoria, com duração ([[qualidade-governanca]]).
- Núcleo de cálculo/filtro é **puro e testável** sem banco/rede (fakes — ver [[principios-solid]]).
