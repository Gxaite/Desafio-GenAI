"""Adapter Postgres de RepositorioAuditoria — persiste a trilha do agente.

Governança/transparência (vault/qualidade-governanca.md): cada execução vira uma linha
em `auditoria.agente_run` e um evento por passo em `auditoria.agente_evento`. Falha aqui
é logada mas NÃO derruba o relatório (a auditoria é observabilidade, não caminho crítico).
"""

from __future__ import annotations

from datetime import date

import psycopg
import structlog

from srag_report.domain.models import EventoAuditoria

log = structlog.get_logger()

_DDL = """
CREATE SCHEMA IF NOT EXISTS auditoria;

CREATE TABLE IF NOT EXISTS auditoria.agente_run (
    run_id       text PRIMARY KEY,
    referencia   date,
    executado_em timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auditoria.agente_evento (
    id      bigserial PRIMARY KEY,
    run_id  text NOT NULL REFERENCES auditoria.agente_run(run_id) ON DELETE CASCADE,
    ordem   int  NOT NULL,
    no      text NOT NULL,
    tipo    text NOT NULL,
    detalhe text,
    ts      timestamptz NOT NULL
);
"""


class PostgresRepositorioAuditoria:
    """Implementa `RepositorioAuditoria` sobre o Postgres."""

    def __init__(self, database_url: str) -> None:
        self._dsn = database_url

    def registrar(
        self, run_id: str, referencia: date | None, eventos: list[EventoAuditoria]
    ) -> None:
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                conn.execute(_DDL)
                conn.execute(
                    "INSERT INTO auditoria.agente_run (run_id, referencia) VALUES (%s, %s) "
                    "ON CONFLICT (run_id) DO NOTHING",
                    (run_id, referencia),
                )
                with conn.cursor() as cur:
                    cur.executemany(
                        "INSERT INTO auditoria.agente_evento "
                        "(run_id, ordem, no, tipo, detalhe, ts) VALUES (%s, %s, %s, %s, %s, %s)",
                        [
                            (run_id, i, e.no, e.tipo, e.detalhe, e.ts)
                            for i, e in enumerate(eventos)
                        ],
                    )
                conn.commit()
        except psycopg.Error as exc:  # observabilidade: loga, não propaga
            log.warning("auditoria.falha", run_id=run_id, erro=str(exc))
