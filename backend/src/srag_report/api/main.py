"""API FastAPI — ponto de entrada do serviço backend.

Fase 1: apenas health checks. As rotas do agente/relatório entram nas Fases 5-6.
"""

from __future__ import annotations

from fastapi import FastAPI

from srag_report.config.settings import settings

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
