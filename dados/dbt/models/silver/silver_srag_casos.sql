-- SILVER: casos de SRAG limpos, tipados e deduplicados (1 linha por notificação).
-- Ainda a nível de caso — não sai do banco; só a camada GOLD (agregada) é servida.

with bruto as (

    select * from {{ source('bronze', 'srag_raw') }}

),

limpo as (

    select
        nu_notific,
        cast(substr(dt_sin_pri, 1, 10) as date)   as dt_sintomas,
        coalesce(nullif(sg_uf, ''), 'NA')          as uf,
        nullif(evolucao, '')                       as evolucao,
        nullif(uti, '')                            as uti,
        nullif(vacina_cov, '')                     as vacina_cov
    from bruto
    -- descarta registros sem data de sintoma válida (base das séries e taxas)
    where dt_sin_pri is not null
      and length(dt_sin_pri) >= 10
      and nu_notific is not null

),

deduplicado as (

    -- salvaguarda: 1 linha por notificação (os arquivos-fonte já são disjuntos)
    select
        *,
        row_number() over (partition by nu_notific order by dt_sintomas) as _rn
    from limpo

)

select
    nu_notific,
    dt_sintomas,
    uf,
    evolucao,
    uti,
    vacina_cov
from deduplicado
where _rn = 1
