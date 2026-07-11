"""Filtro de relevância de notícias — guardrail puro (vault/qualidade-governanca.md).

O LLM só narra sobre notícias que passam por aqui; ruído fora do tema SRAG é descartado
antes de chegar ao agente.
"""

from __future__ import annotations

from srag_report.domain.models import Noticia

# Termos ASCII que casam mesmo em texto acentuado (ex.: "respirat" em "respiratória").
TERMOS_SRAG = (
    "srag", "respirat", "gripe", "influenza", "covid", "sars", "vsr", "surto",
)


def e_relevante(noticia: Noticia, termos: tuple[str, ...] = TERMOS_SRAG) -> bool:
    texto = f"{noticia.titulo} {noticia.descricao or ''}".lower()
    return any(termo in texto for termo in termos)


def filtrar_relevantes(
    noticias: list[Noticia], termos: tuple[str, ...] = TERMOS_SRAG
) -> list[Noticia]:
    return [n for n in noticias if e_relevante(n, termos)]
