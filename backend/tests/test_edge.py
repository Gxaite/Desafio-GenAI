"""Casos de borda: virada de ano, mart vazio e falha explícita da fonte de notícias."""

from __future__ import annotations

from datetime import date

import pytest

from srag_report.application.orchestration import construir_grafo, executar
from srag_report.application.tools import _inicio_12_meses, calcular_metricas, dados_grafico
from srag_report.domain.errors import ErroDados, ErroFonteNoticias
from srag_report.domain.models import AgregadoSRAG, Noticia, Periodo, PontoSerie

REF = date(2026, 7, 5)


def test_janela_12_meses_vira_o_ano() -> None:
    assert _inicio_12_meses(date(2026, 7, 5)) == date(2025, 8, 1)
    assert _inicio_12_meses(date(2026, 1, 15)) == date(2025, 2, 1)  # janeiro → ano anterior
    assert _inicio_12_meses(date(2026, 12, 31)) == date(2026, 1, 1)


class _RepoVazio:
    def data_mais_recente(self) -> date | None:
        return None

    def agregado(self, periodo: Periodo) -> AgregadoSRAG:
        return AgregadoSRAG()

    def serie_diaria(self, periodo: Periodo) -> list[PontoSerie]:
        return []

    def serie_mensal(self, periodo: Periodo) -> list[PontoSerie]:
        return []


def test_mart_vazio_falha_explicita() -> None:
    with pytest.raises(ErroDados):
        calcular_metricas(_RepoVazio())
    with pytest.raises(ErroDados):
        dados_grafico(_RepoVazio())


class _Repo:
    def data_mais_recente(self) -> date | None:
        return REF

    def agregado(self, periodo: Periodo) -> AgregadoSRAG:
        return AgregadoSRAG(casos=100, ev_cura=90, ev_obito=5, ev_obito_outras=5,
                            uti_sim=25, uti_nao=75, vac_sim=38, vac_nao=62)

    def serie_diaria(self, periodo: Periodo) -> list[PontoSerie]:
        return [PontoSerie(competencia=REF, casos=10)]

    def serie_mensal(self, periodo: Periodo) -> list[PontoSerie]:
        return [PontoSerie(competencia=date(2025, 8, 1), casos=100)]


class _FonteQuebrada:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        raise ErroFonteNoticias("indisponível")


class _LLM:
    def completar(self, system: str, user: str) -> str:
        return "ok"


def test_agente_falha_quando_noticias_indisponiveis() -> None:
    """Sem fallback: fonte de notícias fora do ar falha a execução, não gera relatório vazio."""
    with pytest.raises(ErroFonteNoticias):
        executar(construir_grafo(_Repo(), _FonteQuebrada(), _LLM()))
