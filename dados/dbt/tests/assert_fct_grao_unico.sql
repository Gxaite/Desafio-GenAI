-- Grão do fato: no máximo uma linha por (dt, uf). Falha se houver duplicata.
select
    dt,
    uf,
    count(*) as n
from {{ ref('fct_srag_diario') }}
group by dt, uf
having count(*) > 1
