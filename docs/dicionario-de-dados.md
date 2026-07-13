# Dicionário de dados — SRAG

Documenta a **fonte** (Open DATASUS / SIVEP-Gripe), os **campos de origem** usados e a **camada
gold** que este projeto criou e serve. Complementa a documentação por camada em
[`../dados/dbt/models`](../dados/dbt/models) e o site navegável do `dbt docs`.

## 1. Fonte

- **Dataset:** SRAG 2019 a 2026 (SIVEP-Gripe), Open DATASUS — <https://opendatasus.saude.gov.br>.
- **Arquivos usados:** `INFLUD25` (2025) e `INFLUD26` (2026), CSV `;`, 194 colunas, UTF-8, datas ISO 8601.
- **Dicionário oficial (cópia local):**
  [`data/reference/dicionario-de-dados-srag-2019-2025.pdf`](../data/reference/dicionario-de-dados-srag-2019-2025.pdf)
  e [`ficha-de-notificacao-srag-2025.pdf`](../data/reference/ficha-de-notificacao-srag-2025.pdf).

## 2. Campos de origem utilizados

Das 194 colunas, entram no `bronze` apenas as necessárias às métricas (minimização, LGPD):

| Campo (origem) | Significado | Valores relevantes | Uso |
|---|---|---|---|
| `NU_NOTIFIC` | Número da notificação | identificador do registro | chave de deduplicação |
| `DT_SIN_PRI` | Data dos primeiros sintomas | data (ISO) | base das séries e da taxa de aumento |
| `SG_UF` | UF de residência | sigla (`SP`, `RJ`, …) | recorte geográfico (dado sensível) |
| `EVOLUCAO` | Desfecho do caso | `1` cura · `2` óbito · `3` óbito outras causas · `9` ignorado | mortalidade |
| `UTI` | Internado em UTI? | `1` sim · `2` não · `9` ignorado | proxy de ocupação de UTI |
| `VACINA_COV` | Vacinado (COVID)? | `1` sim · `2` não · `9` ignorado | proxy de vacinação |

## 3. Camada gold (o que servimos)

View de serviço `gold.gold_mart_srag_diario` — grão **(dia do 1º sintoma, UF)**, só agregados
(nenhum dado a nível de indivíduo cruza a fronteira):

| Coluna | Tipo | Significado |
|---|---|---|
| `dt` | date | Data do 1º sintoma (`DT_SIN_PRI`). |
| `uf` | text | Sigla da UF (`NA` quando ausente). |
| `uf_nome`, `regiao` | text | Nome e região da UF (via seed `dim_uf`). |
| `casos` | bigint | Total de casos (notificações) no dia/UF. |
| `ev_cura`, `ev_obito`, `ev_obito_outras` | bigint | Casos por desfecho (`EVOLUCAO` 1/2/3). |
| `uti_sim`, `uti_nao` | bigint | Casos com UTI = sim / não. |
| `vac_sim`, `vac_nao` | bigint | Casos vacinados / não vacinados. |

Modelagem completa (dimensões `dim_uf`/`dim_data`, fato `fct_srag_diario`) em
[`../dados/dbt/models/gold`](../dados/dbt/models/gold).

## 4. Métricas e o que é o **N**

Todas as taxas são calculadas em Python puro (`backend/.../domain/metrics.py`). O **N** exibido
é o **denominador** de cada taxa — quantos registros entraram no cálculo. Denominadores usam
**apenas valores conhecidos** (1 ou 2); `9 = ignorado` e ausentes ficam de fora (por isso o N é
menor que o total de casos).

| Métrica | Fórmula | N (denominador) |
|---|---|---|
| Taxa de aumento de casos | `(casos_atual − casos_anterior) / casos_anterior` | casos do período anterior de igual duração |
| Taxa de mortalidade | `ev_obito / (ev_cura + ev_obito + ev_obito_outras)` | casos com desfecho conhecido |
| Taxa de ocupação de UTI | `uti_sim / (uti_sim + uti_nao)` | casos com status de UTI conhecido |
| Taxa de vacinação | `vac_sim / (vac_sim + vac_nao)` | casos com status de vacinação conhecido |

## 5. Ressalvas importantes

- **UTI e vacinação são proxies POR CASO.** A base traz o status por paciente, não leitos totais
  (ocupação hospitalar) nem população (cobertura vacinal). São proporções entre os casos de SRAG
  com status conhecido — dados reais, mas com denominador diferente da definição "clássica".
- **Dias recentes são provisórios.** Casos com `DT_SIN_PRI` recente ainda não receberam todas as
  notificações (atraso de notificação), então a cauda da série é subnotificada. O tratamento
  desses dias é descrito em [`../vault/dominio/metricas.md`](../vault/dominio/metricas.md).
