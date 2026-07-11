"""Testes de observabilidade: duração por nó na trilha e modelos de leitura de execução."""

from __future__ import annotations

from datetime import UTC, date, datetime

from srag_report.application.orchestration import construir_grafo, executar
from srag_report.domain.models import (
    AgregadoSRAG,
    EventoAuditoria,
    ExecucaoAgente,
    Metrica,
    Noticia,
    Periodo,
    PontoSerie,
    ResumoExecucao,
)

REF = date(2026, 7, 5)


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


class _Fonte:
    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        return [Noticia(titulo="SRAG sobe", fonte="G1", url="http://x")]


class _LLM:
    def completar(self, system: str, user: str) -> str:
        return "ok"


def test_trilha_registra_duracao_por_no() -> None:
    estado = executar(construir_grafo(_Repo(), _Fonte(), _LLM()))
    assert len(estado["trilha"]) == 4
    for evento in estado["trilha"]:
        assert evento.duracao_ms is not None
        assert evento.duracao_ms >= 0


def test_modelos_de_leitura_da_execucao() -> None:
    agora = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)
    execucao = ExecucaoAgente(
        run_id="abc", referencia=REF, executado_em=agora,
        eventos=[EventoAuditoria(no="metricas", tipo="tool", detalhe="4", ts=agora, duracao_ms=12)],
        metricas=[Metrica(nome="Mortalidade", valor=5.0, unidade="%", denominador=100)],
        noticias=[Noticia(titulo="SRAG", fonte="G1", url="http://x")],
    )
    assert execucao.eventos[0].duracao_ms == 12
    assert execucao.metricas[0].valor == 5.0
    assert execucao.noticias[0].fonte == "G1"

    resumo = ResumoExecucao(run_id="abc", referencia=REF, executado_em=agora, n_eventos=4)
    assert resumo.n_eventos == 4
