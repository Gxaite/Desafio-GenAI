"""Testes do grafo do agente (LangGraph) com repositório/fonte/LLM fakes — sem rede."""

from __future__ import annotations

from datetime import date

import pytest

from srag_report.application.orchestration import construir_grafo, executar
from srag_report.domain.errors import ErroFonteNoticias, ErroModeloLLM
from srag_report.domain.models import AgregadoSRAG, Noticia, Periodo, PontoSerie

REF = date(2026, 7, 5)


class _FakeRepo:
    def data_mais_recente(self) -> date | None:
        return REF

    def agregado(self, periodo: Periodo, uf: str | None = None) -> AgregadoSRAG:
        if periodo.fim == REF:
            return AgregadoSRAG(casos=100, ev_cura=90, ev_obito=5, ev_obito_outras=5,
                                uti_sim=25, uti_nao=75, vac_sim=38, vac_nao=62)
        return AgregadoSRAG(casos=80)

    def serie_diaria(self, periodo: Periodo) -> list[PontoSerie]:
        return [PontoSerie(competencia=REF, casos=10)]

    def serie_mensal(self, periodo: Periodo) -> list[PontoSerie]:
        return [PontoSerie(competencia=date(2025, 8, 1), casos=100)]


class _FakeFonte:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        return [Noticia(titulo="Casos de SRAG sobem", fonte="G1", url="http://x")]


class _FakeLLM:
    def completar(self, system: str, user: str) -> str:
        return "Narrativa do LLM sobre a situação de SRAG."


class _LLMQuebrado:
    def completar(self, system: str, user: str) -> str:
        raise ErroModeloLLM("indisponível")


class _FonteQuebrada:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        raise ErroFonteNoticias("indisponível")


def test_grafo_produz_relatorio_completo() -> None:
    grafo = construir_grafo(_FakeRepo(), _FakeFonte(), _FakeLLM())
    estado = executar(grafo)

    assert estado["metricas"] is not None and len(estado["metricas"]) == 4
    assert estado["series"] is not None and estado["series"].diaria_30d
    assert estado["noticias"] and estado["noticias"][0].fonte == "G1"
    assert estado["narrativa"] == "Narrativa do LLM sobre a situação de SRAG."
    assert [e.no for e in estado["trilha"]] == [
        "metricas", "graficos", "noticias", "narrativa", "avaliacao",
    ]
    assert estado["run_id"]


def test_grafo_propaga_erro_quando_llm_falha() -> None:
    """Sem fallback: falha do LLM sobe como erro, não vira narrativa determinística."""
    grafo = construir_grafo(_FakeRepo(), _FakeFonte(), _LLMQuebrado())
    with pytest.raises(ErroModeloLLM):
        executar(grafo)


def test_grafo_propaga_erro_quando_noticias_falham() -> None:
    """Sem fallback: falha da fonte de notícias sobe como erro, não vira lista vazia."""
    grafo = construir_grafo(_FakeRepo(), _FonteQuebrada(), _FakeLLM())
    with pytest.raises(ErroFonteNoticias):
        executar(grafo)
