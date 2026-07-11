-- Testa o grão do mart: no máximo uma linha por (dt, uf). Falha se houver duplicata.
select
    dt,
    uf,
    count(*) as n
from {{ ref('gold_mart_srag_diario') }}
group by dt, uf
having count(*) > 1
