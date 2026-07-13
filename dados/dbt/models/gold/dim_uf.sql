-- DIM: unidades federativas (código → nome + região), a partir do seed versionado.
select
    uf,
    uf_nome,
    regiao
from {{ ref('seed_uf') }}
