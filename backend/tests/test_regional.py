"""Teste da análise regional (métricas por UF + notícias + overview do LLM), com fakes."""

from __future__ import annotations

from datetime import date

import pytest

from srag_report.application.regional import analise_regional
from srag_report.domain.errors import ErroFonteNoticias
from srag_report.domain.models import AgregadoSRAG, Noticia, Periodo


class _Repo:
    def data_mais_recente(self) -> date | None:
        return date(2026, 7, 5)

    def agregado(self, periodo: Periodo, uf: str | None = None) -> AgregadoSRAG:
        return AgregadoSRAG(casos=40, ev_cura=90, ev_obito=5, ev_obito_outras=5,
                            uti_sim=25, uti_nao=75, vac_sim=38, vac_nao=62)


class _Fonte:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        return [Noticia(titulo="SRAG sobe em São Paulo", fonte="G1", url="http://x")]


class _LLM:
    def __init__(self) -> None:
        self.prompts: list[tuple[str, str]] = []

    def completar(self, system: str, user: str) -> str:
        self.prompts.append((system, user))
        return "Panorama regional de teste."


def test_analise_regional_gera_overview() -> None:
    llm = _LLM()
    r = analise_regional(_Repo(), _Fonte(), llm, "SP", "São Paulo", foco="UTI", dias_provisorios=14)
    assert r.uf == "SP" and r.uf_nome == "São Paulo"
    assert r.overview == "Panorama regional de teste."
    assert len(r.metricas) == 4
    assert r.referencia == date(2026, 6, 21)  # 05/07 recuado 14 dias
    system, user = llm.prompts[0]
    assert "São Paulo" in user and "UTI" in user


class _FonteQuebrada:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        raise ErroFonteNoticias("429")


class _NoticiasRepo:
    def salvar(self, noticias: list[Noticia]) -> int:
        return 0

    def listar(self, limite: int = 50, fonte: str | None = None,
               desde: date | None = None) -> list[Noticia]:
        return [Noticia(titulo="SRAG no histórico do banco", fonte="Banco", url="http://h")]

    def serie_mensal(self, desde: date | None = None) -> list:
        return []

    def fontes(self) -> list[str]:
        return []


def test_analise_regional_usa_banco_quando_newsapi_falha() -> None:
    llm = _LLM()
    r = analise_regional(_Repo(), _FonteQuebrada(), llm, "SP", "São Paulo",
                         noticias_repo=_NoticiasRepo())
    assert r.overview == "Panorama regional de teste."
    assert "SRAG no histórico do banco" in llm.prompts[0][1]


def test_analise_regional_sem_historico_propaga_erro() -> None:
    """Sem repositório de notícias e NewsAPI fora, o erro sobe (não inventa dados)."""
    with pytest.raises(ErroFonteNoticias):
        analise_regional(_Repo(), _FonteQuebrada(), _LLM(), "SP", "São Paulo")
