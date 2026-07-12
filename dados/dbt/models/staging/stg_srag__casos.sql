-- STAGING: 1:1 com a fonte bronze. Renomeia, tipa e normaliza vazios (view).
-- Sem dedup nem regra de negócio — isso é do intermediate/marts.

with fonte as (

    select * from {{ source('bronze', 'srag_raw') }}

)

select
    nullif(nu_notific, '') as nu_notificacao,
    cast(substr(dt_sin_pri, 1, 10) as date) as dt_sintomas,
    upper(coalesce(nullif(trim(sg_uf), ''), 'NA')) as uf,
    nullif(evolucao, '') as evolucao,
    nullif(uti, '') as uti,
    nullif(vacina_cov, '') as vacina_covid,
    arquivo_origem
from fonte
where
    dt_sin_pri is not null
    and length(dt_sin_pri) >= 10
    and nu_notific is not null
