"""Grafo LangGraph do agente (linear, MVP) e o runner.

Fluxo: métricas → gráficos → notícias → narrativa. Cada nó é um ponto de auditoria
(adr-0005). Degradação graciosa: notícias/LLM podem falhar sem derrubar o relatório.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import Any

from langgraph.graph import END, START, StateGraph

from srag_report.application import narrativa as narr
from srag_report.application.orchestration.state import EstadoRelatorio, EventoAuditoria
from srag_report.application.tools import buscar_noticias, calcular_metricas, dados_grafico
from srag_report.domain.errors import ErroFonteNoticias, ErroGuardrail, ErroModeloLLM
from srag_report.domain.ports import FonteNoticias, ModeloLLM, RepositorioDados


def _evento(no: str, tipo: str, detalhe: str) -> EventoAuditoria:
    return EventoAuditoria(no=no, tipo=tipo, detalhe=detalhe, ts=datetime.now(UTC))


class _Nos:
    """Nós do grafo com as dependências injetadas (composition root as instancia)."""

    def __init__(self, repo: RepositorioDados, fonte: FonteNoticias, llm: ModeloLLM) -> None:
        self._repo = repo
        self._fonte = fonte
        self._llm = llm

    def metricas(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        ref = estado.get("referencia") or self._repo.data_mais_recente()
        ms = calcular_metricas(self._repo, ref)
        return {"referencia": ref, "metricas": ms,
                "trilha": [_evento("metricas", "tool", f"{len(ms)} métricas calculadas")]}

    def graficos(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        series = dados_grafico(self._repo, estado.get("referencia"))
        detalhe = f"{len(series.diaria_30d)} dias, {len(series.mensal_12m)} meses"
        return {"series": series, "trilha": [_evento("graficos", "tool", detalhe)]}

    def noticias(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        try:
            ns = buscar_noticias(self._fonte)
            return {"noticias": ns,
                    "trilha": [_evento("noticias", "tool", f"{len(ns)} relevantes")]}
        except ErroFonteNoticias as exc:  # degrada: relatório sai sem notícias
            return {"noticias": [],
                    "trilha": [_evento("noticias", "fallback", str(exc))]}

    def narrativa(self, estado: EstadoRelatorio) -> EstadoRelatorio:
        metricas = estado.get("metricas") or []
        noticias = estado.get("noticias") or []
        system, user = narr.montar_prompt(metricas, noticias, estado.get("referencia"))
        try:
            texto = narr.validar_narrativa(self._llm.completar(system, user))
            return {"narrativa": texto,
                    "trilha": [_evento("narrativa", "llm", f"{len(texto)} caracteres")]}
        except (ErroModeloLLM, ErroGuardrail) as exc:  # degrada: narrativa determinística
            texto = narr.narrativa_fallback(metricas, estado.get("referencia"))
            return {"narrativa": texto,
                    "trilha": [_evento("narrativa", "fallback", str(exc))]}


def construir_grafo(repo: RepositorioDados, fonte: FonteNoticias, llm: ModeloLLM) -> Any:
    """Compila o grafo linear com as dependências injetadas."""
    nos = _Nos(repo, fonte, llm)
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
