"""Adapter Postgres do RepositorioDados — lê a camada gold (mart agregado).

Só leitura e só agregados. Traduz erros de psycopg em ErroDados na fronteira.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import psycopg

from srag_report.domain.errors import ErroDados
from srag_report.domain.models import AgregadoSRAG, AgregadoUF, Periodo, PontoSerie

_MART = "gold.gold_mart_srag_diario"

_COLUNAS_AGREGADO = (
    "casos", "ev_cura", "ev_obito", "ev_obito_outras",
    "uti_sim", "uti_nao", "vac_sim", "vac_nao",
)


class PostgresRepositorioDados:
    """Implementa `RepositorioDados` sobre o Postgres."""

    def __init__(self, database_url: str) -> None:
        self._dsn = database_url

    def data_mais_recente(self) -> date | None:
        # Nome da tabela é constante interna; valores são sempre parametrizados (%s).
        row = self._um(f"SELECT max(dt) FROM {_MART}")  # nosec B608
        return row[0] if row else None

    def agregado(self, periodo: Periodo, uf: str | None = None) -> AgregadoSRAG:
        somas = ", ".join(f"coalesce(sum({c}), 0)" for c in _COLUNAS_AGREGADO)
        sql = f"SELECT {somas} FROM {_MART} WHERE dt BETWEEN %s AND %s"  # nosec B608
        params: list[Any] = [periodo.inicio, periodo.fim]
        if uf:
            sql += " AND uf = %s"
            params.append(uf)
        row = self._um(sql, tuple(params))
        valores = row if row else (0,) * len(_COLUNAS_AGREGADO)
        return AgregadoSRAG(**dict(zip(_COLUNAS_AGREGADO, valores, strict=True)))

    def agregado_por_uf(self, periodo: Periodo) -> list[AgregadoUF]:
        # Taxas calculadas no banco (mesmas fórmulas das métricas), só para o mapa.
        sql = (
            "SELECT uf, max(uf_nome), max(regiao), coalesce(sum(casos), 0), "
            "round(100.0*sum(ev_obito)/nullif(sum(ev_cura+ev_obito+ev_obito_outras), 0), 2), "
            "round(100.0*sum(uti_sim)/nullif(sum(uti_sim+uti_nao), 0), 2), "
            "round(100.0*sum(vac_sim)/nullif(sum(vac_sim+vac_nao), 0), 2) "
            f"FROM {_MART} WHERE dt BETWEEN %s AND %s GROUP BY uf ORDER BY 4 DESC"  # nosec B608
        )
        rows = self._todos(sql, (periodo.inicio, periodo.fim))
        return [
            AgregadoUF(
                uf=r[0], uf_nome=r[1] or r[0], regiao=r[2] or "Desconhecida",
                casos=int(r[3]),
                mortalidade=None if r[4] is None else float(r[4]),
                uti=None if r[5] is None else float(r[5]),
                vacinacao=None if r[6] is None else float(r[6]),
            )
            for r in rows
        ]

    def serie_diaria(self, periodo: Periodo) -> list[PontoSerie]:
        return self._serie(
            f"SELECT dt, sum(casos) FROM {_MART} WHERE dt BETWEEN %s AND %s "  # nosec B608
            "GROUP BY dt ORDER BY dt",
            periodo,
        )

    def serie_mensal(self, periodo: Periodo) -> list[PontoSerie]:
        return self._serie(
            f"SELECT date_trunc('month', dt)::date, sum(casos) FROM {_MART} "  # nosec B608
            "WHERE dt BETWEEN %s AND %s GROUP BY 1 ORDER BY 1",
            periodo,
        )

    # ── internos ──
    def _serie(self, sql: str, periodo: Periodo) -> list[PontoSerie]:
        rows = self._todos(sql, (periodo.inicio, periodo.fim))
        return [PontoSerie(competencia=r[0], casos=int(r[1])) for r in rows]

    def _um(self, sql: str, params: tuple[Any, ...] = ()) -> tuple[Any, ...] | None:
        with self._conectar() as conn:
            return conn.execute(sql, params).fetchone()

    def _todos(self, sql: str, params: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
        with self._conectar() as conn:
            return conn.execute(sql, params).fetchall()

    def _conectar(self) -> psycopg.Connection:
        try:
            return psycopg.connect(self._dsn, connect_timeout=5)
        except psycopg.Error as exc:  # fronteira: SDK → erro de domínio
            raise ErroDados(f"falha ao conectar no Postgres: {exc}") from exc
