# Qualidade e Governança (atributos transversais)

Concerns que atravessam todas as camadas da [[arquitetura]] e atacam diretamente os critérios
de avaliação do desafio: **Governança/Transparência, Guardrails, Dados Sensíveis e Clean Code**.

## Governança e Auditoria

Critério **"registro de decisões dos agentes"**. Cada execução gera uma **trilha estruturada
(JSON)**, registrando por evento:

- `timestamp`, `no` (nó do grafo), `tipo` (decisão / tool_call / llm);
- entrada, saída (ou resumo), modelo usado, duração;
- erros (a execução falha explicitamente; não há fallback que os oculte).

O grafo do [[agente-orquestrador]] favorece isso: cada nó é um ponto de log. Um `run_id`
correlaciona toda a trilha de uma execução.

**Transparência no output:** o relatório traz rodapé com modelo, fontes de notícias e timestamp;
premissas metodológicas explícitas (proxies — [[adr-0007-metricas-proxy]]); contagens de limpeza
do ETL ([[camada-dados]]). O próprio vault **é parte da governança**: as ADRs documentam *por que*
cada decisão foi tomada, não só *o quê*.

## Guardrails

Camadas que impedem resultados incorretos, inventados ou inseguros:

1. **Entrada** — validação de parâmetros via pydantic ([[camada-tools]]).
2. **Grounding obrigatório** — o LLM só narra sobre números vindos das tools; **nunca calcula
   nem inventa métricas** ([[adr-0004-llm-orquestra-python-calcula]]).
3. **Relevância de notícias** — filtro de tema (SRAG/saúde) antes de usar.
4. **Saída** — validar que toda métrica citada na narrativa existe no estado; sinalizar divergências.
5. **Dados sensíveis** — bloquear qualquer vazamento a nível de indivíduo.
6. **Falha explícita** — na ausência de dado, retornar erro/`N/A` em vez de improvisar.

Violação levanta `ErroGuardrail`. Guardrails **previnem** o que a auditoria **registra**.

## Dados Sensíveis (LGPD)

Os microdados do [[srag-datasus]] são dados pessoais sensíveis de saúde (LGPD, art. 5º, II).

- **Minimização** — carregar só as colunas necessárias às [[metricas]] (de 194 para ~15).
- **Só agregados cruzam a fronteira** — nenhum dado a nível de indivíduo sai da [[camada-dados]];
  tools e relatório operam sobre contagens/taxas.
- **Sem identificadores diretos** — nunca expor combinações reidentificáveis (ex.: município +
  idade/sexo/raça).
- **Segredos fora do código** — chaves (OpenRouter, NewsAPI) via `.env`.
- **Rastreabilidade** — decisões de anonimização registradas na trilha de auditoria.

## Observabilidade

Três pilares, em `src/srag_report/observability/`:

1. **Logs estruturados** — `structlog` emitindo JSON, com `run_id` em todo evento. Nada de `print`.
2. **Tracing** — spans (OpenTelemetry) por nó do grafo e por chamada de adapter, medindo latência
   e propagando o `run_id`.
3. **Trilha de auditoria** — o registro de decisões/tool calls descrito acima.

Injetada via ports/decorators, sem poluir o domínio. Dados sensíveis **nunca** entram em logs.

## Resiliência

Toda borda externa (NewsAPI, LLM/OpenRouter, disco) pode falhar; o sistema tenta se recuperar de
falhas **transitórias** e, esgotadas as tentativas, **falha explicitamente** — sem fallback que
mascare o problema ([[adr-0010-resiliencia]]).

| Padrão | Onde | Como |
|---|---|---|
| **Timeout** | todo I/O externo | limite explícito por chamada; nunca esperar infinito |
| **Retry + backoff com jitter** | NewsAPI, LLM | `tenacity`; só erros transitórios (5xx, timeout, rate-limit) |
| **Fail-fast (sem fallback)** | orquestração | erro tipado sobe; API responde 503 / evento de erro no stream — sem relatório degradado |
| **Erros tipados na fronteira** | NewsAPI, LLM | SDK vira `SragReportError`; o domínio nunca vê exceção de infra |
| **Idempotência** | ETL | mesma entrada → mesma saída; reprocessar é seguro |

Resiliência é responsabilidade da **infraestrutura**; o domínio permanece puro. I/O nas bordas é
assíncrono ([[adr-0011-async-io]]).

## Tratamento de Erros

Erros são explícitos e tipados. Hierarquia em `domain/errors.py`:

```
SragReportError                 # base
├── ErroDados                   # ETL/repositório: dado ausente, coluna inválida
├── ErroFonteNoticias           # NewsAPI indisponível/limite
├── ErroModeloLLM               # falha do LLM/OpenRouter
├── ErroGuardrail               # violação de validação/grounding
└── ErroConfiguracao            # config/segredo ausente (fail-fast no boot)
```

- **Fronteira traduz** — adapters capturam exceções de SDK e relançam como erro de domínio; o
  domínio nunca vê `requests.HTTPError`.
- **Transitório vs permanente** — transitório → retry; permanente → falha clara.
- **Sem `except:` nu**, sem engolir exceção; todo erro tratado é logado.
- **Config inválida falha no boot**, não em runtime.

## Clean Code e Tooling

Portões automatizados que sustentam o critério *Clean Code* ([[adr-0009-tooling-uv-ruff-mypy]]):

| Área | Ferramenta | Papel |
|---|---|---|
| Pacote/venv | **uv** | rápido, lockfile determinístico, PEP 621 |
| Lint + format | **ruff** | substitui flake8/black/isort |
| Tipagem | **mypy --strict** | type safety de ponta a ponta |
| Testes | **pytest** + `pytest-cov` | unit (domínio) + integração (adapters) |
| Fronteiras de import | **import-linter** | impõe as regras do hexágono |
| Hooks | **pre-commit** | roda ruff/mypy antes do commit |
| CI | **GitHub Actions** | lint + type + test em cada push |
| Tarefas | **justfile** | `just up`, `just etl`, `just test`, `just lint` |

**Estratégia de testes:** domínio ([[metricas]]) testado sem mocks (casos de dados sujos);
adapters via fakes/gravações (sem chamar APIs reais no CI); guardrails com testes provando que
dado inventado é bloqueado. Docstrings + type hints em APIs públicas; commits convencionais.
