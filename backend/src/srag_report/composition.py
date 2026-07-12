"""Composition root — monta os adapters concretos a partir da config (12-factor).

Único lugar que conhece implementações concretas; API e CLI consomem daqui.

Observabilidade de LLM: via OpenRouter Broadcast para o LangSmith (config no painel do
OpenRouter, sem código). A observabilidade do grafo fica na trilha de auditoria própria.
"""

from __future__ import annotations

from typing import NamedTuple

from srag_report.config.settings import settings
from srag_report.domain.ports import (
    FonteNoticias,
    ModeloLLM,
    RenderizadorRelatorio,
    RepositorioAuditoria,
    RepositorioDados,
    RepositorioNoticias,
)
from srag_report.infrastructure.audit.postgres_audit import PostgresRepositorioAuditoria
from srag_report.infrastructure.data.postgres_repo import PostgresRepositorioDados
from srag_report.infrastructure.llm.openrouter_client import OpenRouterModeloLLM
from srag_report.infrastructure.news.newsapi_client import NewsApiFonteNoticias
from srag_report.infrastructure.news.postgres_noticias import PostgresRepositorioNoticias
from srag_report.infrastructure.report.renderer import RelatorioPdfRenderer


class Deps(NamedTuple):
    repo: RepositorioDados
    fonte: FonteNoticias
    llm: ModeloLLM
    auditoria: RepositorioAuditoria
    renderizador: RenderizadorRelatorio
    noticias: RepositorioNoticias


def montar_dependencias() -> Deps:
    return Deps(
        repo=PostgresRepositorioDados(settings.database_url),
        fonte=NewsApiFonteNoticias(settings.newsapi_key),
        llm=OpenRouterModeloLLM(
            settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            model=settings.openrouter_model_narrative,
        ),
        auditoria=PostgresRepositorioAuditoria(settings.database_url),
        renderizador=RelatorioPdfRenderer(),
        noticias=PostgresRepositorioNoticias(settings.database_url),
    )
