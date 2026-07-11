"""Use case: gerar o relatório de SRAG em PDF.

Roda o grafo do agente e delega a renderização a um `RenderizadorRelatorio` (port).
Devolve também o estado (com a trilha de auditoria) para logging/governança.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from srag_report.application.orchestration import construir_grafo, executar
from srag_report.application.orchestration.state import EstadoRelatorio
from srag_report.domain.models import DadosRelatorio, SeriesGraficos
from srag_report.domain.ports import (
    FonteNoticias,
    ModeloLLM,
    RenderizadorRelatorio,
    RepositorioAuditoria,
    RepositorioDados,
)


def gerar_relatorio_pdf(
    repo: RepositorioDados,
    fonte: FonteNoticias,
    llm: ModeloLLM,
    modelo: str,
    renderizador: RenderizadorRelatorio,
    referencia: date | None = None,
    auditoria: RepositorioAuditoria | None = None,
) -> tuple[bytes, EstadoRelatorio]:
    grafo = construir_grafo(repo, fonte, llm)
    estado = executar(grafo, referencia)

    if auditoria is not None:  # persiste a trilha (governança) — nunca bloqueia o relatório
        auditoria.registrar(estado["run_id"], estado["referencia"], estado["trilha"])

    dados = DadosRelatorio(
        referencia=estado["referencia"],
        metricas=estado["metricas"] or [],
        series=estado["series"] or SeriesGraficos(diaria_30d=[], mensal_12m=[]),
        noticias=estado["noticias"] or [],
        narrativa=estado["narrativa"] or "",
        run_id=estado["run_id"],
        modelo=modelo,
        gerado_em=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    )
    return renderizador.renderizar(dados), estado
