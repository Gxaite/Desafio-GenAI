"""Adapter Postgres de RepositorioNoticias — histórico de notícias (explorador).

Acumula as notícias coletadas ao longo do tempo, deduplicando por URL, para um histórico
navegável independente de cada execução do agente.
"""

from __future__ import annotations

import psycopg

from srag_report.domain.errors import ErroDados
from srag_report.domain.models import Noticia

_DDL = """
CREATE SCHEMA IF NOT EXISTS noticias;

CREATE TABLE IF NOT EXISTS noticias.historico (
    id           serial PRIMARY KEY,
    titulo       text NOT NULL,
    fonte        text,
    url          text UNIQUE,
    publicado_em date,
    descricao    text,
    capturado_em timestamptz NOT NULL DEFAULT now()
);
"""


class PostgresRepositorioNoticias:
    """Implementa `RepositorioNoticias` sobre o Postgres."""

    def __init__(self, database_url: str) -> None:
        self._dsn = database_url

    def salvar(self, noticias: list[Noticia]) -> int:
        novas = 0
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                conn.execute(_DDL)
                with conn.cursor() as cur:
                    for n in noticias:
                        if not n.url:  # sem URL não há como deduplicar; ignora
                            continue
                        cur.execute(
                            "INSERT INTO noticias.historico "
                            "(titulo, fonte, url, publicado_em, descricao) "
                            "VALUES (%s, %s, %s, %s, %s) "
                            "ON CONFLICT (url) DO NOTHING RETURNING id",
                            (n.titulo, n.fonte, n.url, n.publicado_em, n.descricao),
                        )
                        if cur.fetchone() is not None:
                            novas += 1
                conn.commit()
        except psycopg.Error as exc:  # fronteira: SDK → erro de domínio
            raise ErroDados(f"falha ao salvar notícias: {exc}") from exc
        return novas

    def listar(self, limite: int = 50, fonte: str | None = None) -> list[Noticia]:
        sql = (
            "SELECT titulo, fonte, url, publicado_em, descricao, capturado_em "
            "FROM noticias.historico "
        )
        params: tuple[object, ...] = ()
        if fonte:
            sql += "WHERE fonte = %s "
            params = (fonte,)
        sql += "ORDER BY coalesce(publicado_em::timestamptz, capturado_em) DESC LIMIT %s"
        params = (*params, limite)
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                conn.execute(_DDL)
                rows = conn.execute(sql, params).fetchall()
        except psycopg.Error as exc:
            raise ErroDados(f"falha ao listar notícias: {exc}") from exc
        return [
            Noticia(titulo=r[0], fonte=r[1] or "", url=r[2] or "", publicado_em=r[3],
                    descricao=r[4], capturado_em=r[5])
            for r in rows
        ]
