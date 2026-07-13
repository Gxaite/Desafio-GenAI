-- SILVER: casos de SRAG limpos, tipados, deduplicados (1 linha/notificação) + flags de
-- negócio. Une o que antes era staging (tipagem 1:1) e intermediate (dedup + flags) numa
-- única tabela da camada. Ainda a nível de caso — NÃO sai do banco; só a GOLD (agregada)
-- é servida ao backend/Grafana. Denominadores das taxas usam só valores conhecidos (1/2).

with bruto as (

    select * from {{ source('bronze', 'srag_raw') }}

),

limpo as (

    select
        nullif(nu_notific, '') as nu_notificacao,
        cast(substr(dt_sin_pri, 1, 10) as date) as dt_sintomas,
        upper(coalesce(nullif(trim(sg_uf), ''), 'NA')) as uf,
        nullif(evolucao, '') as evolucao,
        nullif(uti, '') as uti,
        nullif(vacina_cov, '') as vacina_covid
    from bruto
    where
        dt_sin_pri is not null
        and length(dt_sin_pri) >= 10
        and nu_notific is not null

),

deduplicado as (

    -- salvaguarda: 1 linha por notificação (os arquivos-fonte já são disjuntos)
    select
        *,
        row_number() over (partition by nu_notificacao order by dt_sintomas) as _rn
    from limpo

)

select
    nu_notificacao,
    dt_sintomas,
    uf,
    evolucao,
    uti,
    vacina_covid,
    (evolucao = '1') as is_cura,
    (evolucao = '2') as is_obito,
    (evolucao = '3') as is_obito_outras,
    (evolucao in ('1', '2', '3')) as desfecho_conhecido,
    (uti = '1') as foi_uti,
    (uti in ('1', '2')) as uti_conhecida,
    (vacina_covid = '1') as vacinado,
    (vacina_covid in ('1', '2')) as vacina_conhecida
from deduplicado
where _rn = 1
