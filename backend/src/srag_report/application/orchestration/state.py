"""Estado do grafo + evento de auditoria. Ver vault/qualidade-governanca.md."""

from __future__ import annotations

import operator
from datetime import date
from typing import Annotated, TypedDict

from srag_report.domain.models import EventoAuditoria, Metrica, Noticia, SeriesGraficos


class EstadoRelatorio(TypedDict, total=False):
    """Estado que flui pelo grafo. `trilha` acumula (reducer add)."""

    run_id: str
    referencia: date | None
    metricas: list[Metrica] | None
    series: SeriesGraficos | None
    noticias: list[Noticia] | None
    narrativa: str | None
    avaliacao: str | None
    trilha: Annotated[list[EventoAuditoria], operator.add]

