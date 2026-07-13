"""Use case do explorador de notícias: coleta variada (várias consultas) e persiste no histórico."""

from __future__ import annotations

from srag_report.application.tools import buscar_noticias
from srag_report.domain.models import Noticia
from srag_report.domain.ports import FonteNoticias, RepositorioNoticias

# Consultas diversas ampliam a variedade de fontes/veículos frente a uma única busca.
_CONSULTAS = (
    "SRAG",
    "síndrome respiratória aguda grave",
    "influenza",
    "gripe",
    "covid",
    "vírus sincicial respiratório",
    "doenças respiratórias",
    "surto respiratório",
    "internações respiratórias",
    "vacina gripe",
)


def atualizar_historico(
    fonte: FonteNoticias,
    repo: RepositorioNoticias,
    *,
    limite_por_consulta: int = 20,
) -> int:
    """Busca notícias relevantes em várias consultas, deduplica por URL e salva. Retorna novas."""
    vistas: set[str] = set()
    coletadas: list[Noticia] = []
    for consulta in _CONSULTAS:
        for n in buscar_noticias(fonte, consulta, limite=limite_por_consulta):
            if n.url and n.url not in vistas:
                vistas.add(n.url)
                coletadas.append(n)
    return repo.salvar(coletadas)
