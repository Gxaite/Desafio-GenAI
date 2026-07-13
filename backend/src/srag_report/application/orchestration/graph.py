"""Grafo LangGraph do agente (linear, MVP) e o runner.

Fluxo: métricas → gráficos → notícias → narrativa. Cada nó é um ponto de auditoria
(adr-0005). Sem fallback: se qualquer nó falhar (dados, notícias ou LLM), o erro sobe e
a execução falha explicitamente — nada de relatório silenciosamente degradado (adr-0010).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import Any

from langgraph.graph import END, START, StateGraph

from srag_report.application import narrativa as narr
from srag_report.application.orchestration.state import EstadoRelatorio
from srag_report.application.tools import (
    buscar_noticias,
    calcular_metricas,
    dados_grafico,
    referencia_efetiva,
)
from srag_report.domain.models import EventoAuditoria
from srag_report.domain.ports import FonteNoticias, ModeloLLM, RepositorioDados


def _evento(no: str, tipo: str, detalhe: str, inicio: datetime) -> EventoAuditoria:
    agora = datetime.now(UTC)
    return EventoAuditoria(
        no=no, tipo=tipo, detalhe=detalhe, ts=agora,
        duracao_ms=int((agora - inicio).total_seconds() * 1000),
    )


class _Nos:
    """Nós do grafo com as dependências injetadas (composition root as instancia)."""

    def __init__(
        self, repo: RepositorioDados, fonte: FonteNoticias, llm: ModeloLLM,
        dias_provisorios: int = 0,
    ) -> None:
        self._repo = repo
        self._fonte = fonte
        self._llm = llm
        self._dias_provisorios = dias_provisorios

    def metricas(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        t0 = datetime.now(UTC)
        ref = estado.get("referencia") or referencia_efetiva(
            self._repo, None, self._dias_provisorios
        )
        ms = calcular_metricas(self._repo, ref)
        return {"referencia": ref, "metricas": ms,
                "trilha": [_evento("metricas", "tool", f"{len(ms)} métricas calculadas", t0)]}

    def graficos(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        t0 = datetime.now(UTC)
        series = dados_grafico(self._repo, estado.get("referencia"))
        detalhe = f"{len(series.diaria_30d)} dias, {len(series.mensal_12m)} meses"
        return {"series": series, "trilha": [_evento("graficos", "tool", detalhe, t0)]}

    def noticias(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        t0 = datetime.now(UTC)
        ns = buscar_noticias(self._fonte)  # ErroFonteNoticias sobe e falha a execução
        return {"noticias": ns,
                "trilha": [_evento("noticias", "tool", f"{len(ns)} relevantes", t0)]}

    def narrativa(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        t0 = datetime.now(UTC)
        metricas = estado.get("metricas") or []
        noticias = estado.get("noticias") or []
        system, user = narr.montar_prompt(metricas, noticias, estado.get("referencia"))
        # ErroModeloLLM/ErroGuardrail sobem e falham a execução — sem narrativa determinística
        texto = narr.validar_narrativa(self._llm.completar(system, user))
        return {"narrativa": texto,
                "trilha": [_evento("narrativa", "llm", f"{len(texto)} caracteres", t0)]}


def construir_grafo(
    repo: RepositorioDados, fonte: FonteNoticias, llm: ModeloLLM, dias_provisorios: int = 0
) -> Any:
    """Compila o grafo linear com as dependências injetadas."""
    nos = _Nos(repo, fonte, llm, dias_provisorios)
    g: Any = StateGraph(EstadoRelatorio)  # builder do LangGraph — cola de framework
    g.add_node("metricas", nos.metricas)
    g.add_node("graficos", nos.graficos)
    g.add_node("noticias", nos.noticias)
    g.add_node("narrativa", nos.narrativa)
    g.add_edge(START, "metricas")
    g.add_edge("metricas", "graficos")
    g.add_edge("graficos", "noticias")
    g.add_edge("noticias", "narrativa")
    g.add_edge("narrativa", END)
    return g.compile()


def executar(grafo: Any, referencia: date | None = None) -> EstadoRelatorio:
    """Roda o grafo com um `run_id` novo e a trilha zerada."""
    estado_inicial: EstadoRelatorio = {
        "run_id": uuid.uuid4().hex,
        "referencia": referencia,
        "trilha": [],
    }
    resultado: EstadoRelatorio = grafo.invoke(estado_inicial)
    return resultado
