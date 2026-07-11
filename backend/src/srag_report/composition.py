"""Composition root — monta os adapters concretos a partir da config (12-factor).

Único lugar que conhece implementações concretas; API e CLI consomem daqui.
"""

from __future__ import annotations

import os

import structlog

from srag_report.config.settings import settings
from srag_report.domain.ports import (
    FonteNoticias,
    ModeloLLM,
    RenderizadorRelatorio,
    RepositorioAuditoria,
    RepositorioDados,
)
from srag_report.infrastructure.audit.postgres_audit import PostgresRepositorioAuditoria
from srag_report.infrastructure.data.postgres_repo import PostgresRepositorioDados
from srag_report.infrastructure.llm.openrouter_client import OpenRouterModeloLLM
from srag_report.infrastructure.news.newsapi_client import NewsApiFonteNoticias
from srag_report.infrastructure.report.renderer import RelatorioPdfRenderer

log = structlog.get_logger()


def ativar_langsmith() -> bool:
    """Liga o tracing LangSmith se houver chave. Idempotente. Retorna se ativou."""
    if not settings.langchain_api_key:
        return False
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
    os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)
    os.environ.setdefault("LANGCHAIN_ENDPOINT", settings.langchain_endpoint)
    log.info("langsmith.ativo", project=settings.langchain_project)
    return True


def montar_dependencias() -> tuple[
    RepositorioDados, FonteNoticias, ModeloLLM, RepositorioAuditoria, RenderizadorRelatorio
]:
    ativar_langsmith()
    repo = PostgresRepositorioDados(settings.database_url)
    fonte = NewsApiFonteNoticias(settings.newsapi_key)
    llm = OpenRouterModeloLLM(
        settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.openrouter_model_narrative,
    )
    auditoria = PostgresRepositorioAuditoria(settings.database_url)
    renderizador = RelatorioPdfRenderer()
    return repo, fonte, llm, auditoria, renderizador
