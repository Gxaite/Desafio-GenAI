-- INTERMEDIATE: 1 linha por notificação (dedup) + flags derivadas para as métricas.
-- Denominadores das taxas usam só valores conhecidos (1/2), materializado como tabela.

with casos as (

    select
        *,
        row_number() over (partition by nu_notificacao order by dt_sintomas) as _rn
    from {{ ref('stg_srag__casos') }}

)

select
    nu_notificacao,
    dt_sintomas,
    uf,
    evolucao,
    uti,
    vacina_covid,
    (evolucao = '1')             as is_cura,
    (evolucao = '2')             as is_obito,
    (evolucao = '3')             as is_obito_outras,
    (evolucao in ('1', '2', '3')) as desfecho_conhecido,
    (uti = '1')                  as foi_uti,
    (uti in ('1', '2'))          as uti_conhecida,
    (vacina_covid = '1')         as vacinado,
    (vacina_covid in ('1', '2')) as vacina_conhecida
from casos
where _rn = 1
