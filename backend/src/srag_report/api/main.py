"""API FastAPI — ponto de entrada do serviço backend.

Rotas: health checks, métricas (JSON) e relatório (PDF gerado pelo agente).
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Response

from srag_report.application.orchestration import construir_grafo
from srag_report.application.relatorio import gerar_relatorio_pdf
from srag_report.application.tools import calcular_metricas
from srag_report.composition import montar_dependencias
from srag_report.config.settings import settings
from srag_report.domain.errors import SragReportError
from srag_report.domain.models import ExecucaoAgente, Metrica, ResumoExecucao

app = FastAPI(title="SRAG Report API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness — o serviço está de pé."""
    return {"status": "ok"}


@app.get("/health/db")
def health_db() -> dict[str, str]:
    """Readiness — o Postgres está acessível."""
    try:
        import psycopg

        with psycopg.connect(settings.database_url, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "db": "reachable"}
    except Exception as exc:  # noqa: BLE001 — health check reporta, não propaga
        return {"status": "degraded", "db": type(exc).__name__}


@app.get("/metricas")
def metricas() -> list[Metrica]:
    """As 4 métricas dos últimos 30 dias (JSON)."""
    repo, _fonte, _llm, _aud, _rend = montar_dependencias()
    try:
        return calcular_metricas(repo)
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/agente/grafo", response_class=Response)
def agente_grafo() -> Response:
    """Diagrama do grafo do agente (Mermaid) — visualização do fluxo de orquestração."""
    repo, fonte, llm, _aud, _rend = montar_dependencias()
    mermaid = construir_grafo(repo, fonte, llm).get_graph().draw_mermaid()
    return Response(content=mermaid, media_type="text/plain; charset=utf-8")


@app.get("/auditoria/execucoes")
def listar_execucoes(limite: int = 20) -> list[ResumoExecucao]:
    """Execuções recentes do agente (observabilidade)."""
    _repo, _fonte, _llm, auditoria, _rend = montar_dependencias()
    try:
        return auditoria.listar_execucoes(limite)
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/auditoria/execucoes/{run_id}")
def obter_execucao(run_id: str) -> ExecucaoAgente:
    """Detalhe de uma execução: trilha (com durações), métricas e fontes usadas."""
    _repo, _fonte, _llm, auditoria, _rend = montar_dependencias()
    try:
        execucao = auditoria.obter_execucao(run_id)
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if execucao is None:
        raise HTTPException(status_code=404, detail="execução não encontrada")
    return execucao


@app.post("/relatorio")
def relatorio() -> Response:
    """Gera o relatório completo (métricas + gráficos + narrativa) em PDF."""
    repo, fonte, llm, auditoria, renderizador = montar_dependencias()
    try:
        pdf, estado = gerar_relatorio_pdf(
            repo, fonte, llm, settings.openrouter_model_narrative, renderizador,
            auditoria=auditoria,
        )
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    nome = f"relatorio-srag-{estado['referencia']}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{nome}"',
            "X-Run-Id": estado["run_id"] or "",
        },
    )
