# Princípios SOLID no projeto

Onde cada princípio aparece no código (com arquivo) e a **decisão/trade-off** associada.
O hexágono ([[arquitetura]]) já força a maior parte disto; o import-linter e os *fakes* dos
testes são a prova de que não é só teoria.

## S — Single Responsibility
Um arquivo, uma razão para mudar.
- `domain/metrics.py` só calcula; `infrastructure/data/postgres_repo.py` só lê o Postgres;
  `infrastructure/news/newsapi_client.py` só fala com a NewsAPI; `report/{charts,pdf_renderer,
  renderer}.py` separam **gerar gráfico**, **renderizar PDF** e **compor** em passos distintos.
- **Trade-off:** mais arquivos pequenos (esforço de navegação), em troca de mudanças isoladas
  e testáveis sem efeito colateral. Escala bem quando o time cresce.

## O — Open/Closed
Aberto a extensão, fechado a modificação.
- Trocar de LLM, de fonte de notícias ou de renderizador = **novo adapter** implementando o
  `Protocol` em `domain/ports.py`, sem tocar em domínio nem aplicação.
- **Custo de oportunidade:** exige definir os *ports* antes (mais desenho inicial); paga-se
  isso na hora de adicionar/trocar integrações sem risco de regressão no núcleo.

## L — Liskov Substitution
Qualquer implementação de um *port* substitui outra sem quebrar o consumidor.
- Provado nos testes: `FakeRepo`, `FakeFonte`, `FakeLLM`, `FakeRenderer` (em `tests/`) entram
  no lugar dos adapters reais e o agente roda igual — os `Protocol` garantem o contrato.
- **Trade-off:** disciplina de manter o contrato estável; em troca, testes rápidos sem banco/rede.

## I — Interface Segregation
*Ports* pequenos e focados, não uma interface gorda.
- `RepositorioDados`, `FonteNoticias`, `ModeloLLM`, `RepositorioAuditoria`,
  `RenderizadorRelatorio` — cada consumidor depende só do que usa (ex.: `/metricas` usa apenas
  `RepositorioDados`).
- **Trade-off:** mais interfaces, em troca de acoplamento mínimo e mocks triviais.

## D — Dependency Inversion
O núcleo depende de abstrações; detalhes concretos ficam na borda.
- Domínio e aplicação importam **apenas** `domain/ports.py`; a ligação concreta é montada em
  `composition.py` (composition root). Regra **imposta no CI** pelo `import-linter`
  ([[qualidade-governanca]]).
- **Custo de oportunidade:** uma camada de indireção (ports + injeção); em troca, dá para trocar
  Postgres/NewsAPI/OpenRouter sem tocar na lógica — e o domínio é testado sem infraestrutura.

## Por que isso importa aqui
Facilita **crescer**: novos indicadores entram como funções puras em `domain/metrics.py`;
novas integrações como adapters. **Exige mais esforço** de desenho inicial (ports, injeção) e
gera mais arquivos — assumido conscientemente porque o critério de avaliação premia arquitetura
e *Clean Code*, e porque uma PoC que vira produto precisa de fronteiras claras.
