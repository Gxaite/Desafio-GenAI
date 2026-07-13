-- DIM: calendário, cobrindo o intervalo de datas de sintoma observado nos casos.
with limites as (

    select
        min(dt_sintomas) as ini,
        max(dt_sintomas) as fim
    from {{ ref('int_srag__casos_preparados') }}

),

dias as (

    select generate_series(ini, fim, interval '1 day')::date as data
    from limites

)

select
    data,
    extract(year from data)::int as ano,
    extract(month from data)::int as mes,
    to_char(data, 'YYYY-MM') as ano_mes,
    extract(day from data)::int as dia,
    extract(isodow from data)::int as dia_semana,
    extract(week from data)::int as semana_iso
from dias
