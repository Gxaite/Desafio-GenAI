"""Narrativa do relatório — prompt com grounding e validação (guardrails).

O LLM recebe SOMENTE os números já calculados e as notícias já filtradas; é instruído a
não inventar valores. Se o LLM falhar ou a saída não passar no guardrail, o erro sobe e a
execução falha explicitamente — sem narrativa determinística que mascare o problema (adr-0010).
"""

from __future__ import annotations

import re
from datetime import date

from srag_report.domain.errors import ErroGuardrail
from srag_report.domain.models import Metrica, Noticia

_SYSTEM = (
    "Você é um analista de saúde pública escrevendo para leitores não técnicos. Escreva de 2 a 3 "
    "frases claras e diretas, em português simples, explicando o cenário das métricas de SRAG e "
    "citando uma notícia quando fizer sentido. Use somente os números e as fontes fornecidos e "
    "nunca invente dados. Trate as taxas como percentuais entre as pessoas avaliadas, não como "
    "cobertura da população. Evite jargão e rótulos técnicos. Não use títulos, listas nem "
    "marcação de markdown, apenas frases corridas. Não use travessões, dois-pontos nem ponto e "
    "vírgula."
)

_MD_TITULO = re.compile(r"(?m)^\s*#+\s*")  # marcadores de título no início de linha
_MD_ENFASE = re.compile(r"[*_`]+")  # ênfase/código markdown


def _fmt_metrica(m: Metrica) -> str:
    valor = "N/A" if m.valor is None else f"{m.valor}{m.unidade}"
    return f"- {m.nome}: {valor} (base de {m.denominador} pessoas avaliadas)"


def montar_prompt(
    metricas: list[Metrica], noticias: list[Noticia], referencia: date | None
) -> tuple[str, str]:
    linhas_m = "\n".join(_fmt_metrica(m) for m in metricas) or "(sem métricas)"
    linhas_n = "\n".join(f"- {n.titulo} ({n.fonte})" for n in noticias) or "(sem notícias)"
    user = (
        f"Período de referência: {referencia}.\n\n"
        f"Métricas (últimos 30 dias):\n{linhas_m}\n\n"
        f"Notícias recentes sobre SRAG:\n{linhas_n}"
    )
    return _SYSTEM, user


def validar_narrativa(texto: str) -> str:
    """Guardrail de saída: remove marcação de markdown e rejeita narrativa vazia."""
    limpo = _MD_ENFASE.sub("", _MD_TITULO.sub("", texto)).strip()
    if not limpo:
        raise ErroGuardrail("narrativa vazia retornada pelo LLM")
    return limpo
