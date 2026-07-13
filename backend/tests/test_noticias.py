"""Teste do use case do explorador: coleta variada, filtro de relevância e dedup por URL."""

from __future__ import annotations

from datetime import date

from srag_report.application.noticias import atualizar_historico
from srag_report.domain.models import ContagemMensal, Noticia


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

    def listar(
        self, limite: int = 50, fonte: str | None = None, desde: date | None = None
    ) -> list[Noticia]:
        itens = self.recebidas
        if fonte:
            itens = [n for n in itens if n.fonte == fonte]
        return itens[:limite]

    def serie_mensal(self, desde: date | None = None) -> list[ContagemMensal]:
        return [ContagemMensal(competencia=date(2026, 7, 1), total=len(self.recebidas))]

    def fontes(self) -> list[str]:
        return sorted({n.fonte for n in self.recebidas if n.fonte})


def test_atualiza_deduplica_por_url_e_filtra_relevancia() -> None:
    from srag_report.application.noticias import _CONSULTAS

    repo = _Repo()
    novas = atualizar_historico(_Fonte(), repo)

    urls = [n.url for n in repo.recebidas]
    # N consultas -> N URLs únicas + 1 compartilhada (dedup); a irrelevante é filtrada
    assert novas == len(repo.recebidas) == len(_CONSULTAS) + 1
    assert urls.count("http://shared/1") == 1
    assert not any("irrelevante" in u for u in urls)
