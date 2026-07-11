"""Estado do grafo + evento de auditoria. Ver vault/qualidade-governanca.md."""

from __future__ import annotations

import operator
from datetime import date, datetime
from typing import Annotated, TypedDict

from pydantic import BaseModel

from srag_report.domain.models import Metrica, Noticia, SeriesGraficos


class EventoAuditoria(BaseModel):
    """Um evento da trilha de auditoria (uma linha por passo do agente)."""

    no: str
    tipo: str  # tool | llm | fallback | decisao
    detalhe: str
    ts: datetime


class EstadoRelatorio(TypedDict, total=False):
    """Estado que flui pelo grafo. `trilha` acumula (reducer add)."""

    run_id: str
    referencia: date | None
    metricas: list[Metrica] | None
    series: SeriesGraficos | None
    noticias: list[Noticia] | None
    narrativa: str | None
    trilha: Annotated[list[EventoAuditoria], operator.add]
