"""Testes do use case gerar_relatorio_pdf com fakes (sem infra real)."""

from __future__ import annotations

from datetime import date

from srag_report.application.relatorio import gerar_relatorio_pdf, gerar_relatorio_stream
from srag_report.domain.models import (
    AgregadoSRAG,
    DadosRelatorio,
    EventoAuditoria,
    Metrica,
    Noticia,
    Periodo,
    PontoSerie,
)

REF = date(2026, 7, 5)


class _Repo:
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


class _Fonte:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        return [Noticia(titulo="Casos de SRAG sobem", fonte="G1", url="http://x")]


class _LLM:
    def completar(self, system: str, user: str) -> str:
        return "Narrativa gerada."


class _Render:
    def __init__(self) -> None:
        self.recebido: DadosRelatorio | None = None

    def renderizar(self, dados: DadosRelatorio) -> bytes:
        self.recebido = dados
        return b"%PDF-fake"


class _Aud:
    def __init__(self) -> None:
        self.run_id: str | None = None
        self.n_metricas = 0
        self.n_noticias = 0

    def registrar(self, run_id: str, referencia: date | None,
                  eventos: list[EventoAuditoria], metricas: list[Metrica],
                  noticias: list[Noticia], narrativa: str = "",
                  avaliacao: str = "", modelo: str = "", provedor: str = "",
                  tokens: int = 0) -> None:
        self.run_id = run_id
        self.n_eventos = len(eventos)
        self.n_metricas = len(metricas)
        self.n_noticias = len(noticias)
        self.narrativa = narrativa
        self.avaliacao = avaliacao
        self.tokens = tokens


def test_gera_pdf_monta_dados_e_audita() -> None:
    rend, aud = _Render(), _Aud()
    pdf, estado = gerar_relatorio_pdf(_Repo(), _Fonte(), _LLM(), "modelo-x", rend, auditoria=aud)

    assert pdf == b"%PDF-fake"
    assert rend.recebido is not None
    assert rend.recebido.modelo == "modelo-x"
    assert len(rend.recebido.metricas) == 4
    assert rend.recebido.narrativa == "Narrativa gerada."
    assert rend.recebido.avaliacao == "Narrativa gerada."
    assert aud.run_id == estado["run_id"]
    assert aud.n_eventos == 5
    assert aud.n_metricas == 4
    assert aud.n_noticias == 1


def test_gera_pdf_sem_auditoria() -> None:
    rend = _Render()
    pdf, _ = gerar_relatorio_pdf(_Repo(), _Fonte(), _LLM(), "m", rend)
    assert pdf == b"%PDF-fake"


def test_stream_emite_eventos_por_no_e_pdf_no_fim() -> None:
    eventos = list(gerar_relatorio_stream(_Repo(), _Fonte(), _LLM(), "m", _Render()))
    passos = [e["no"] for e in eventos if e["tipo"] == "evento"]
    assert passos == ["metricas", "graficos", "noticias", "narrativa", "avaliacao"]
    fim = eventos[-1]
    assert fim["tipo"] == "fim" and fim["run_id"] and fim["pdf_b64"]
