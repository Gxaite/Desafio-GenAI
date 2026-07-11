"""Use case: gerar o relatório de SRAG em PDF.

Roda o grafo do agente e renderiza o estado resultante (métricas + gráficos + narrativa)
num PDF. Devolve também o estado (com a trilha de auditoria) para logging/governança.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from srag_report.application.orchestration import construir_grafo, executar
from srag_report.application.orchestration.state import EstadoRelatorio
from srag_report.domain.models import SeriesGraficos
from srag_report.domain.ports import (
    FonteNoticias,
    ModeloLLM,
    RepositorioAuditoria,
    RepositorioDados,
)
from srag_report.infrastructure.report.charts import graficos_data_uri
from srag_report.infrastructure.report.pdf_renderer import renderar_pdf


def gerar_relatorio_pdf(
    repo: RepositorioDados,
    fonte: FonteNoticias,
    llm: ModeloLLM,
    modelo: str,
    referencia: date | None = None,
    auditoria: RepositorioAuditoria | None = None,
) -> tuple[bytes, EstadoRelatorio]:
    grafo = construir_grafo(repo, fonte, llm)
    estado = executar(grafo, referencia)

    if auditoria is not None:  # persiste a trilha (governança) — nunca bloqueia o relatório
        auditoria.registrar(estado["run_id"], estado["referencia"], estado["trilha"])

    series = estado["series"] or SeriesGraficos(diaria_30d=[], mensal_12m=[])
    grafico_diario, grafico_mensal = graficos_data_uri(series)

    contexto = {
        "referencia": estado["referencia"],
        "metricas": estado["metricas"] or [],
        "narrativa": estado["narrativa"] or "",
        "noticias": estado["noticias"] or [],
        "grafico_diario": grafico_diario,
        "grafico_mensal": grafico_mensal,
        "run_id": estado["run_id"],
        "modelo": modelo,
        "gerado_em": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    }
    return renderar_pdf(contexto), estado
