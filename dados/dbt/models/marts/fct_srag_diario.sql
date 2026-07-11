-- FATO: grão (dia do 1º sintoma, UF). Medidas aditivas para as métricas/gráficos.
-- FKs: dt → dim_data.data, uf → dim_uf.uf. Só contagens — nenhum microdado.
select
    dt_sintomas                                as dt,
    uf,
    count(*)                                   as casos,
    count(*) filter (where is_cura)            as curas,
    count(*) filter (where is_obito)           as obitos,
    count(*) filter (where is_obito_outras)    as obitos_outras_causas,
    count(*) filter (where foi_uti)            as casos_uti,
    count(*) filter (where uti = '2')          as casos_uti_nao,
    count(*) filter (where vacinado)           as vacinados,
    count(*) filter (where vacina_covid = '2') as nao_vacinados
from {{ ref('int_srag__casos') }}
group by dt_sintomas, uf
