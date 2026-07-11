"""Composition root — monta os adapters concretos a partir da config (12-factor).

Único lugar que conhece implementações concretas; API e CLI consomem daqui.
"""

from __future__ import annotations

from srag_report.config.settings import settings
from srag_report.domain.ports import FonteNoticias, ModeloLLM, RepositorioDados
from srag_report.infrastructure.data.postgres_repo import PostgresRepositorioDados
from srag_report.infrastructure.llm.openrouter_client import OpenRouterModeloLLM
from srag_report.infrastructure.news.newsapi_client import NewsApiFonteNoticias


def montar_dependencias() -> tuple[RepositorioDados, FonteNoticias, ModeloLLM]:
    repo = PostgresRepositorioDados(settings.database_url)
    fonte = NewsApiFonteNoticias(settings.newsapi_key)
    llm = OpenRouterModeloLLM(
        settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.openrouter_model_narrative,
    )
    return repo, fonte, llm
