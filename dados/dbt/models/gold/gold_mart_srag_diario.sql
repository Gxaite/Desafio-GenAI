-- GOLD: mart agregado por (dia, UF). Único artefato servido ao backend e ao Grafana.
-- Só contagens — nenhum dado a nível de indivíduo. As 4 métricas e os 2 gráficos derivam
-- deste mart por SQL (denominadores usam apenas valores conhecidos: 1/2).

select
    dt_sintomas                                          as dt,
    uf,
    count(*)                                             as casos,
    count(*) filter (where evolucao = '1')               as ev_cura,
    count(*) filter (where evolucao = '2')               as ev_obito,
    count(*) filter (where evolucao = '3')               as ev_obito_outras,
    count(*) filter (where uti = '1')                    as uti_sim,
    count(*) filter (where uti = '2')                    as uti_nao,
    count(*) filter (where vacina_cov = '1')             as vac_sim,
    count(*) filter (where vacina_cov = '2')             as vac_nao
from {{ ref('silver_srag_casos') }}
group by dt_sintomas, uf
