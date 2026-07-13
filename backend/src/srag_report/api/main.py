"""API FastAPI — ponto de entrada do serviço backend.

Rotas: health, métricas (JSON), relatório (PDF, bloqueante e streaming), grafo do agente,
auditoria das execuções e explorador de notícias.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, date, datetime, timedelta

import structlog
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse

from srag_report.api.agendador import loop_coleta
from srag_report.api.landing import GRAFO, PAGINA
from srag_report.application.noticias import atualizar_historico
from srag_report.application.orchestration import construir_grafo
from srag_report.application.relatorio import gerar_relatorio_pdf, gerar_relatorio_stream
from srag_report.application.tools import calcular_metricas
from srag_report.composition import montar_dependencias
from srag_report.config.settings import settings
from srag_report.domain.errors import SragReportError
from srag_report.domain.models import (
    ContagemMensal,
    ExecucaoAgente,
    Metrica,
    Noticia,
    ResumoExecucao,
)

log = structlog.get_logger()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Sobe o agendador de coleta de notícias (se habilitado) e o encerra no shutdown."""
    tarefa: asyncio.Task[None] | None = None
    horas = settings.newsapi_intervalo_horas
    if settings.newsapi_key and horas > 0:
        tarefa = asyncio.create_task(loop_coleta(horas))
        log.info("agendador.iniciado", intervalo_horas=horas)
    else:
        log.info("agendador.desativado", tem_chave=bool(settings.newsapi_key), horas=horas)
    try:
        yield
    finally:
        if tarefa is not None:
            tarefa.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await tarefa


app = FastAPI(title="SRAG Report API", version="0.1.0", lifespan=lifespan)


def _desde(dias: int | None) -> date | None:
    """Converte uma janela em dias na data mínima (hoje - dias); None = sem limite."""
    if dias is None or dias <= 0:
        return None
    return (datetime.now(UTC) - timedelta(days=dias)).date()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing() -> str:
    """Página-hub: ponto de entrada único para demonstrar o projeto."""
    return PAGINA


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
    deps = montar_dependencias()
    try:
        return calcular_metricas(deps.repo, dias_provisorios=settings.dados_dias_provisorios)
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/agente/grafo", include_in_schema=False)
def agente_grafo(format: str = "html") -> Response:
    """Fluxo do agente: página HTML (default) ou a fonte Mermaid (?format=mermaid)."""
    if format == "mermaid":
        deps = montar_dependencias()
        mermaid = construir_grafo(deps.repo, deps.fonte, deps.llm).get_graph().draw_mermaid()
        return Response(content=mermaid, media_type="text/plain; charset=utf-8")
    return HTMLResponse(GRAFO)


@app.get("/auditoria/execucoes")
def listar_execucoes(limite: int = 20) -> list[ResumoExecucao]:
    """Execuções recentes do agente (observabilidade)."""
    deps = montar_dependencias()
    try:
        return deps.auditoria.listar_execucoes(limite)
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/auditoria/execucoes/{run_id}")
def obter_execucao(run_id: str) -> ExecucaoAgente:
    """Detalhe de uma execução: trilha (com durações), métricas e fontes usadas."""
    deps = montar_dependencias()
    try:
        execucao = deps.auditoria.obter_execucao(run_id)
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if execucao is None:
        raise HTTPException(status_code=404, detail="execução não encontrada")
    return execucao


@app.get("/noticias")
def noticias(
    limite: int = 50, fonte: str | None = None, dias: int | None = None
) -> list[Noticia]:
    """Histórico de notícias coletadas (explorador), filtrável por fonte e período (dias)."""
    deps = montar_dependencias()
    desde = _desde(dias)
    try:
        return deps.noticias.listar(limite, fonte, desde)
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/noticias/serie")
def noticias_serie(dias: int | None = None) -> list[ContagemMensal]:
    """Volume de notícias por mês (histograma do explorador)."""
    deps = montar_dependencias()
    try:
        return deps.noticias.serie_mensal(_desde(dias))
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/noticias/fontes")
def noticias_fontes() -> list[str]:
    """Fontes distintas no histórico (para o filtro do explorador)."""
    deps = montar_dependencias()
    try:
        return deps.noticias.fontes()
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/noticias/buscar")
def noticias_buscar() -> dict[str, int]:
    """Coleta notícias de várias consultas e salva no histórico. Retorna quantas são novas."""
    deps = montar_dependencias()
    try:
        return {"novas": atualizar_historico(deps.fonte, deps.noticias)}
    except SragReportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/relatorio")
def relatorio() -> Response:
    """Gera o relatório completo (métricas + gráficos + narrativa) em PDF."""
    deps = montar_dependencias()
    try:
        pdf, estado = gerar_relatorio_pdf(
            deps.repo, deps.fonte, deps.llm, settings.openrouter_model_narrative,
            deps.renderizador, auditoria=deps.auditoria,
            dias_provisorios=settings.dados_dias_provisorios,
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


@app.get("/relatorio/stream", include_in_schema=False)
def relatorio_stream() -> StreamingResponse:
    """Gera o relatório emitindo o progresso do agente nó a nó (SSE) e o PDF ao final."""
    deps = montar_dependencias()

    def gen() -> Iterator[str]:
        try:
            for ev in gerar_relatorio_stream(
                deps.repo, deps.fonte, deps.llm, settings.openrouter_model_narrative,
                deps.renderizador, auditoria=deps.auditoria,
                dias_provisorios=settings.dados_dias_provisorios,
            ):
                yield f"data: {json.dumps(ev)}\n\n"
        except SragReportError as exc:
            yield f"data: {json.dumps({'tipo': 'erro', 'msg': str(exc)})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
