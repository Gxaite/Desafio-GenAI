"""Testes da tool de notícias: filtro de relevância (puro) e adapter NewsAPI (mockado)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

import httpx
import pytest

from srag_report.application.tools import buscar_noticias
from srag_report.domain import news
from srag_report.domain.errors import ErroFonteNoticias
from srag_report.domain.models import Noticia
from srag_report.infrastructure.news.newsapi_client import NewsApiFonteNoticias


def _noticia(titulo: str, descricao: str | None = None) -> Noticia:
    return Noticia(titulo=titulo, fonte="x", url="http://x", descricao=descricao)


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


# ── filtro de relevância (puro) ──

def test_filtro_mantem_so_tema_srag() -> None:
    ns = [_noticia("Casos de SRAG sobem"), _noticia("Receita de bolo"),
          _noticia("Nova variante de COVID")]
    assert len(news.filtrar_relevantes(ns)) == 2


def test_filtro_olha_descricao() -> None:
    ns = [_noticia("Alerta epidemiológico", descricao="aumento de casos respiratórios")]
    assert len(news.filtrar_relevantes(ns)) == 1


# ── adapter NewsAPI ──

def test_adapter_parseia_artigos() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.headers["X-Api-Key"] == "k"
        return httpx.Response(200, json={"articles": [
            {"title": "SRAG em alta", "source": {"name": "G1"}, "url": "http://g1",
             "publishedAt": "2026-07-01T10:00:00Z", "description": "casos respiratórios"},
        ]})

    ns = NewsApiFonteNoticias("k", client=_client(handler)).buscar("SRAG")
    assert ns[0].titulo == "SRAG em alta"
    assert ns[0].fonte == "G1"
    assert ns[0].publicado_em == date(2026, 7, 1)


def test_adapter_sem_chave_falha_explicitamente() -> None:
    """Sem fallback: chave ausente vira ErroFonteNoticias, não lista vazia silenciosa."""
    with pytest.raises(ErroFonteNoticias):
        NewsApiFonteNoticias("").buscar("SRAG")


def test_adapter_erro_transitorio_vira_erro_dominio() -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    with pytest.raises(ErroFonteNoticias):
        NewsApiFonteNoticias("k", client=_client(handler)).buscar("SRAG")


# ── tool (composição) ──

def test_tool_aplica_filtro_de_relevancia() -> None:
    class _Fake:
        def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
            return [_noticia("SRAG sobe no país"), _noticia("Futebol hoje")]

    assert len(buscar_noticias(_Fake())) == 1
