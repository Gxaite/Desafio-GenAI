"""Gráficos do relatório com Plotly, exportados como PNG (data URI) para embutir no PDF.

Os 2 gráficos exigidos: casos diários (30d) e mensais (12m). Ver adr-0015 / vault.
"""

from __future__ import annotations

import base64

import plotly.graph_objects as go

from srag_report.domain.models import PontoSerie, SeriesGraficos

_LARGURA, _ALTURA = 900, 340


def _barras(pontos: list[PontoSerie], titulo: str, cor: str) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=[p.competencia for p in pontos],
            y=[p.casos for p in pontos],
            marker_color=cor,
        )
    )
    fig.update_layout(
        title=titulo,
        template="plotly_white",
        margin={"l": 50, "r": 20, "t": 50, "b": 40},
        height=_ALTURA,
        width=_LARGURA,
        font={"size": 13},
    )
    fig.update_yaxes(title_text="casos")
    return fig


def _png_data_uri(fig: go.Figure) -> str:
    png = fig.to_image(format="png", scale=2)
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def graficos_data_uri(series: SeriesGraficos) -> tuple[str, str]:
    """(gráfico diário, gráfico mensal) como data URIs PNG."""
    diario = _barras(series.diaria_30d, "Casos diários (últimos 30 dias)", "#2563eb")
    mensal = _barras(series.mensal_12m, "Casos mensais (últimos 12 meses)", "#7c3aed")
    return _png_data_uri(diario), _png_data_uri(mensal)
