"""Ports (interfaces) do domínio — implementadas por adapters na infraestrutura.

O domínio depende destas abstrações, nunca de SDKs concretos (DIP).
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from srag_report.domain.models import AgregadoSRAG, Noticia, Periodo, PontoSerie


class RepositorioDados(Protocol):
    """Acesso de leitura aos marts agregados (camada gold)."""

    def data_mais_recente(self) -> date | None:
        """Data do registro mais recente no mart (âncora dos períodos)."""
        ...

    def agregado(self, periodo: Periodo) -> AgregadoSRAG:
        """Soma das contagens no período (nacional)."""
        ...

    def serie_diaria(self, periodo: Periodo) -> list[PontoSerie]:
        """Casos por dia no período."""
        ...

    def serie_mensal(self, periodo: Periodo) -> list[PontoSerie]:
        """Casos por mês no período."""
        ...


class FonteNoticias(Protocol):
    """Fonte externa de notícias (ex.: NewsAPI)."""

    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        """Notícias mais recentes para a consulta. Pode retornar [] (degradação)."""
        ...
