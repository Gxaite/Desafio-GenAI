"""Teste do use case do explorador: coleta variada, filtro de relevância e dedup por URL."""

from __future__ import annotations

from srag_report.application.noticias import atualizar_historico
from srag_report.domain.models import Noticia


class _Fonte:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        # uma notícia única por consulta + uma compartilhada (mesma URL em todas)
        return [
            Noticia(titulo=f"SRAG em {consulta}", fonte="G1", url=f"http://u/{consulta}"),
            Noticia(titulo="Gripe avança no país", fonte="Terra", url="http://shared/1"),
            Noticia(titulo="Receita de bolo", fonte="X", url="http://irrelevante"),
        ]


class _Repo:
    def __init__(self) -> None:
        self.recebidas: list[Noticia] = []

    def salvar(self, noticias: list[Noticia]) -> int:
        self.recebidas = noticias
        return len(noticias)

    def listar(self, limite: int = 50, fonte: str | None = None) -> list[Noticia]:
        return self.recebidas[:limite]


def test_atualiza_deduplica_por_url_e_filtra_relevancia() -> None:
    repo = _Repo()
    novas = atualizar_historico(_Fonte(), repo)

    urls = [n.url for n in repo.recebidas]
    # 4 consultas -> 4 URLs únicas + 1 compartilhada; a irrelevante é filtrada
    assert novas == len(repo.recebidas) == 5
    assert urls.count("http://shared/1") == 1
    assert not any("irrelevante" in u for u in urls)
