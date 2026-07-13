"""Adapter Postgres de RepositorioAuditoria — persiste e lê a trilha do agente.

Governança/observabilidade (vault/qualidade-governanca.md): cada execução grava a trilha
(com duração por nó), as métricas e as fontes de notícias usadas. A escrita nunca derruba o
relatório; a leitura (endpoints de observabilidade) traduz falhas em ErroDados.
"""

from __future__ import annotations

from datetime import date

import psycopg
import structlog

from srag_report.domain.errors import ErroDados
from srag_report.domain.models import (
    EventoAuditoria,
    ExecucaoAgente,
    Metrica,
    Noticia,
    ResumoExecucao,
)

log = structlog.get_logger()

_DDL = """
CREATE SCHEMA IF NOT EXISTS auditoria;

CREATE TABLE IF NOT EXISTS auditoria.agente_run (
    run_id       text PRIMARY KEY,
    referencia   date,
    executado_em timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE auditoria.agente_run ADD COLUMN IF NOT EXISTS narrativa text;
ALTER TABLE auditoria.agente_run ADD COLUMN IF NOT EXISTS avaliacao text;
ALTER TABLE auditoria.agente_run ADD COLUMN IF NOT EXISTS modelo text;
ALTER TABLE auditoria.agente_run ADD COLUMN IF NOT EXISTS provedor text;
ALTER TABLE auditoria.agente_run ADD COLUMN IF NOT EXISTS tokens integer;

CREATE TABLE IF NOT EXISTS auditoria.agente_evento (
    id      bigserial PRIMARY KEY,
    run_id  text NOT NULL REFERENCES auditoria.agente_run(run_id) ON DELETE CASCADE,
    ordem   int  NOT NULL,
    no      text NOT NULL,
    tipo    text NOT NULL,
    detalhe text,
    ts      timestamptz NOT NULL
);
ALTER TABLE auditoria.agente_evento ADD COLUMN IF NOT EXISTS duracao_ms integer;

CREATE TABLE IF NOT EXISTS auditoria.agente_metrica (
    id          bigserial PRIMARY KEY,
    run_id      text NOT NULL REFERENCES auditoria.agente_run(run_id) ON DELETE CASCADE,
    nome        text NOT NULL,
    valor       double precision,
    unidade     text,
    denominador bigint
);

CREATE TABLE IF NOT EXISTS auditoria.agente_noticia (
    id     bigserial PRIMARY KEY,
    run_id text NOT NULL REFERENCES auditoria.agente_run(run_id) ON DELETE CASCADE,
    titulo text NOT NULL,
    fonte  text,
    url    text
);
"""


class PostgresRepositorioAuditoria:
    """Implementa `RepositorioAuditoria` sobre o Postgres."""

    def __init__(self, database_url: str) -> None:
        self._dsn = database_url

    def registrar(
        self,
        run_id: str,
        referencia: date | None,
        eventos: list[EventoAuditoria],
        metricas: list[Metrica],
        noticias: list[Noticia],
        narrativa: str = "",
        avaliacao: str = "",
        modelo: str = "",
        provedor: str = "",
        tokens: int = 0,
    ) -> None:
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                conn.execute(_DDL)
                conn.execute(
                    "INSERT INTO auditoria.agente_run "
                    "(run_id, referencia, narrativa, avaliacao, modelo, provedor, tokens) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (run_id) DO NOTHING",
                    (run_id, referencia, narrativa, avaliacao, modelo, provedor, tokens),
                )
                with conn.cursor() as cur:
                    cur.executemany(
                        "INSERT INTO auditoria.agente_evento "
                        "(run_id, ordem, no, tipo, detalhe, ts, duracao_ms) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        [(run_id, i, e.no, e.tipo, e.detalhe, e.ts, e.duracao_ms)
                         for i, e in enumerate(eventos)],
                    )
                    cur.executemany(
                        "INSERT INTO auditoria.agente_metrica "
                        "(run_id, nome, valor, unidade, denominador) VALUES (%s, %s, %s, %s, %s)",
                        [(run_id, m.nome, m.valor, m.unidade, m.denominador) for m in metricas],
                    )
                    cur.executemany(
                        "INSERT INTO auditoria.agente_noticia (run_id, titulo, fonte, url) "
                        "VALUES (%s, %s, %s, %s)",
                        [(run_id, n.titulo, n.fonte, n.url) for n in noticias],
                    )
                conn.commit()
        except psycopg.Error as exc:  # observabilidade: loga, não propaga
            log.warning("auditoria.falha", run_id=run_id, erro=str(exc))

    def listar_execucoes(self, limite: int = 20) -> list[ResumoExecucao]:
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                rows = conn.execute(
                    "SELECT r.run_id, r.referencia, r.executado_em, count(e.id) "
                    "FROM auditoria.agente_run r "
                    "LEFT JOIN auditoria.agente_evento e USING (run_id) "
                    "GROUP BY r.run_id, r.referencia, r.executado_em "
                    "ORDER BY r.executado_em DESC LIMIT %s",
                    (limite,),
                ).fetchall()
        except psycopg.Error as exc:
            raise ErroDados(f"falha ao listar execuções: {exc}") from exc
        return [
            ResumoExecucao(run_id=r[0], referencia=r[1], executado_em=r[2], n_eventos=r[3])
            for r in rows
        ]

    def obter_execucao(self, run_id: str) -> ExecucaoAgente | None:
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                run = conn.execute(
                    "SELECT referencia, executado_em FROM auditoria.agente_run WHERE run_id = %s",
                    (run_id,),
                ).fetchone()
                if run is None:
                    return None
                eventos = conn.execute(
                    "SELECT no, tipo, detalhe, ts, duracao_ms FROM auditoria.agente_evento "
                    "WHERE run_id = %s ORDER BY ordem",
                    (run_id,),
                ).fetchall()
                metricas = conn.execute(
                    "SELECT nome, valor, unidade, denominador FROM auditoria.agente_metrica "
                    "WHERE run_id = %s ORDER BY id",
                    (run_id,),
                ).fetchall()
                noticias = conn.execute(
                    "SELECT titulo, fonte, url FROM auditoria.agente_noticia "
                    "WHERE run_id = %s ORDER BY id",
                    (run_id,),
                ).fetchall()
        except psycopg.Error as exc:
            raise ErroDados(f"falha ao obter execução: {exc}") from exc
        return ExecucaoAgente(
            run_id=run_id,
            referencia=run[0],
            executado_em=run[1],
            eventos=[
                EventoAuditoria(no=e[0], tipo=e[1], detalhe=e[2], ts=e[3], duracao_ms=e[4])
                for e in eventos
            ],
            metricas=[
                Metrica(nome=m[0], valor=m[1], unidade=m[2], denominador=m[3]) for m in metricas
            ],
            noticias=[Noticia(titulo=n[0], fonte=n[1], url=n[2]) for n in noticias],
        )
