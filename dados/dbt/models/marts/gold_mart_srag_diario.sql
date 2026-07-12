-- VIEW DE SERVIÇO: contrato estável consumido pelo backend e pelo Grafana.
-- Denormaliza o fato com dim_uf (nome/região) e mantém os nomes de coluna esperados
-- pela camada de tools (ev_*, uti_*, vac_*).
{{ config(materialized='view') }}

select
    f.dt,
    f.uf,
    d.uf_nome,
    d.regiao,
    f.casos,
    f.curas as ev_cura,
    f.obitos as ev_obito,
    f.obitos_outras_causas as ev_obito_outras,
    f.casos_uti as uti_sim,
    f.casos_uti_nao as uti_nao,
    f.vacinados as vac_sim,
    f.nao_vacinados as vac_nao
from {{ ref('fct_srag_diario') }} as f
left join {{ ref('dim_uf') }} as d using (uf)
