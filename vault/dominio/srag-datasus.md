---
tags: [dominio, dados]
atualizado: 2026-07-09
---

# SRAG / Open DATASUS (SIVEP-Gripe)

## O que é
Base real de **internações por Síndrome Respiratória Aguda Grave (SRAG)** do Open DATASUS
(SIVEP-Gripe). Dataset **"SRAG 2019 a 2026"**. Baixamos **2025** e **2026** em CSV.
Tratamento em [[camada-dados]].

## Arquivos em uso (em `data/raw/srag/`, proveniência no MANIFEST)

| Arquivo | Original | Linhas | Ano |
|---|---|---|---|
| `srag-2025-extracao-2026-07-06.csv` | `INFLUD25-06-07-2026.csv` | ~336k | ~2025 (+ cauda) |
| `srag-2026-extracao-2026-07-06.csv` | `INFLUD26-06-07-2026.csv` | ~155k | 100% 2026 |

- Arquivos **particionados por ano** — um não contém o outro (`NU_NOTIFIC` disjunto entre
  eles). "Últimos 12 meses" exige **os dois**; "últimos 30 dias" usa só o de 2026. Os ~1.649
  registros com `DT_SIN_PRI` em 2026 dentro do arquivo de 2025 são casos distintos (virada de
  ano), **não duplicatas**.
- **Características técnicas:** `;`, campos entre aspas, **194 colunas**, datas **ISO 8601**,
  encoding **UTF-8**. Dicionário em `data/reference/`.

## Colunas confirmadas (presentes no cabeçalho)

| Campo | Uso | Observação |
|---|---|---|
| `DT_SIN_PRI` | data 1ºs sintomas | base das séries e da taxa de aumento |
| `DT_NOTIFIC` / `DT_INTERNA` | notificação / internação | |
| `EVOLUCAO` | desfecho | `2` = óbito → mortalidade (não há `DT_OBITO`; usar `DT_EVOLUCA`) |
| `UTI` | foi para UTI? | `1` = sim → proxy de ocupação ([[adr-0007-metricas-proxy]]) |
| `VACINA` / `VACINA_COV` | vacinado? | status **do caso**, não da população ([[adr-0007-metricas-proxy]]) |
| `CLASSI_FIN` | classificação final | filtrar SRAG confirmada |
| `SG_UF` | UF | geografia — sensível ([[qualidade-governanca]]) |

## Ligações
Como viram números: [[metricas]] · Tratamento/carga: [[camada-dados]] · Privacidade: [[qualidade-governanca]]
