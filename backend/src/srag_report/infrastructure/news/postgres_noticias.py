"""Adapter Postgres de RepositorioNoticias — histórico de notícias (explorador).

Acumula as notícias coletadas ao longo do tempo, deduplicando por URL, para um histórico
navegável independente de cada execução do agente.
"""

from __future__ import annotations

from datetime import date

import psycopg

from srag_report.domain.errors import ErroDados
from srag_report.domain.models import ContagemMensal, Noticia

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

    def listar(
        self, limite: int = 50, fonte: str | None = None, desde: date | None = None
    ) -> list[Noticia]:
        sql = (
            "SELECT titulo, fonte, url, publicado_em, descricao, capturado_em "
            "FROM noticias.historico "
        )
        filtros, params = self._filtros(fonte, desde)
        if filtros:
            sql += "WHERE " + " AND ".join(filtros) + " "
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

    def serie_mensal(self, desde: date | None = None) -> list[ContagemMensal]:
        sql = (
            "SELECT date_trunc('month', "
            "coalesce(publicado_em::timestamptz, capturado_em))::date AS mes, count(*) "
            "FROM noticias.historico "
        )
        filtros, params = self._filtros(None, desde)
        if filtros:
            sql += "WHERE " + " AND ".join(filtros) + " "
        sql += "GROUP BY mes ORDER BY mes"
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                conn.execute(_DDL)
                rows = conn.execute(sql, params).fetchall()
        except psycopg.Error as exc:
            raise ErroDados(f"falha ao agregar notícias: {exc}") from exc
        return [ContagemMensal(competencia=r[0], total=r[1]) for r in rows]

    def fontes(self) -> list[str]:
        sql = (
            "SELECT fonte FROM noticias.historico "
            "WHERE fonte IS NOT NULL AND fonte <> '' GROUP BY fonte ORDER BY count(*) DESC"
        )
        try:
            with psycopg.connect(self._dsn, connect_timeout=5) as conn:
                conn.execute(_DDL)
                rows = conn.execute(sql).fetchall()
        except psycopg.Error as exc:
            raise ErroDados(f"falha ao listar fontes: {exc}") from exc
        return [r[0] for r in rows]

    @staticmethod
    def _filtros(
        fonte: str | None, desde: date | None
    ) -> tuple[list[str], tuple[object, ...]]:
        """Monta cláusulas WHERE parametrizadas (fonte e/ou data mínima)."""
        filtros: list[str] = []
        params: tuple[object, ...] = ()
        if fonte:
            filtros.append("fonte = %s")
            params = (*params, fonte)
        if desde:
            filtros.append(
                "coalesce(publicado_em::timestamptz, capturado_em) >= %s"
            )
            params = (*params, desde)
        return filtros, params
