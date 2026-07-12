"""Narrativa do relatório — prompt com grounding e validação (guardrails).

O LLM recebe SOMENTE os números já calculados e as notícias já filtradas; é instruído a
não inventar valores. Se o LLM falhar ou a saída não passar no guardrail, o erro sobe e a
execução falha explicitamente — sem narrativa determinística que mascare o problema (adr-0010).
"""

from __future__ import annotations

from datetime import date

from srag_report.domain.errors import ErroGuardrail
from srag_report.domain.models import Metrica, Noticia

_SYSTEM = (
    "Você é um analista de saúde pública. Escreva de 2 a 3 frases objetivas, em português, "
    "contextualizando as métricas de SRAG fornecidas e citando uma notícia quando pertinente. "
    "Use somente os números e as fontes fornecidos; nunca invente dados nem cite valores fora "
    "da lista. Vá direto ao ponto, sem introduções e sem travessões."
)


def _fmt_metrica(m: Metrica) -> str:
    valor = "N/A" if m.valor is None else f"{m.valor}{m.unidade}"
    return f"- {m.nome}: {valor} (N={m.denominador})"


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
    """Guardrail de saída: rejeita narrativa vazia."""
    limpo = texto.strip()
    if not limpo:
        raise ErroGuardrail("narrativa vazia retornada pelo LLM")
    return limpo
