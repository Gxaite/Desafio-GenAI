-- Coerência das medidas: não-negativas e sub-contagens não excedem o total de casos.
select *
from {{ ref('fct_srag_diario') }}
where casos < 0
   or least(curas, obitos, obitos_outras_causas,
            casos_uti, casos_uti_nao, vacinados, nao_vacinados) < 0
   or (curas + obitos + obitos_outras_causas) > casos
   or (casos_uti + casos_uti_nao) > casos
   or (vacinados + nao_vacinados) > casos
