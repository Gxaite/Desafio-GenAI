"""Use case: gerar o relatório de SRAG em PDF (modo bloqueante e modo streaming).

Roda o grafo do agente e delega a renderização a um `RenderizadorRelatorio` (port). O modo
streaming emite o progresso nó a nó (para o hub mostrar o agente ao vivo) e entrega o PDF ao fim.
"""

from __future__ import annotations

import base64
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime
from typing import Any

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


def _montar_dados(estado: EstadoRelatorio, modelo: str) -> DadosRelatorio:
    return DadosRelatorio(
        referencia=estado.get("referencia"),
        metricas=estado.get("metricas") or [],
        series=estado.get("series") or SeriesGraficos(diaria_30d=[], mensal_12m=[]),
        noticias=estado.get("noticias") or [],
        narrativa=estado.get("narrativa") or "",
        run_id=estado.get("run_id") or "",
        modelo=modelo,
        gerado_em=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    )


def _persistir(auditoria: RepositorioAuditoria | None, estado: EstadoRelatorio) -> None:
    if auditoria is not None:  # governança — nunca bloqueia o relatório
        auditoria.registrar(
            estado.get("run_id") or "", estado.get("referencia"),
            estado.get("trilha") or [], estado.get("metricas") or [],
            estado.get("noticias") or [],
        )


def gerar_relatorio_pdf(
    repo: RepositorioDados,
    fonte: FonteNoticias,
    llm: ModeloLLM,
    modelo: str,
    renderizador: RenderizadorRelatorio,
    referencia: date | None = None,
    auditoria: RepositorioAuditoria | None = None,
    dias_provisorios: int = 0,
) -> tuple[bytes, EstadoRelatorio]:
    estado = executar(construir_grafo(repo, fonte, llm, dias_provisorios), referencia)
    _persistir(auditoria, estado)
    return renderizador.renderizar(_montar_dados(estado, modelo)), estado


def gerar_relatorio_stream(
    repo: RepositorioDados,
    fonte: FonteNoticias,
    llm: ModeloLLM,
    modelo: str,
    renderizador: RenderizadorRelatorio,
    referencia: date | None = None,
    auditoria: RepositorioAuditoria | None = None,
    dias_provisorios: int = 0,
) -> Iterator[dict[str, Any]]:
    """Executa o grafo emitindo o progresso de cada nó em tempo real; encerra com o PDF."""
    grafo = construir_grafo(repo, fonte, llm, dias_provisorios)
    inicial: EstadoRelatorio = {"run_id": uuid.uuid4().hex, "referencia": referencia, "trilha": []}
    final: EstadoRelatorio = inicial
    emitidos = 0

    for estado in grafo.stream(inicial, stream_mode="values"):
        final = estado
        trilha = estado.get("trilha") or []
        while emitidos < len(trilha):
            ev = trilha[emitidos]
            emitidos += 1
            yield {"tipo": "evento", "no": ev.no, "passo": ev.tipo, "duracao_ms": ev.duracao_ms}

    _persistir(auditoria, final)
    pdf = renderizador.renderizar(_montar_dados(final, modelo))
    yield {"tipo": "fim", "run_id": final.get("run_id") or "",
           "pdf_b64": base64.b64encode(pdf).decode("ascii")}
