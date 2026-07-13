"""Avaliação do relatório — análise complementar gerada pelo LLM.

Recebe os mesmos dados do relatório (métricas + notícias + narrativa) e pede ao LLM uma
avaliação estruturada: qualidade dos dados, tendências, comparações e recomendações.
O resultado vai para a seção "Avaliação do agente" do PDF e para o painel do Grafana.
"""

from __future__ import annotations

from datetime import date

from srag_report.domain.models import Metrica, Noticia

_SYSTEM_AVALIACAO = (
    "Você é um epidemiologista sênior fazendo uma avaliação técnica de um relatório "
    "automatizado de SRAG (Síndrome Respiratória Aguda Grave). Analise os dados fornecidos e "
    "produza uma avaliação estruturada em 4 tópicos (use apenas texto corrido, sem markdown, "
    "sem listas, sem títulos). "
    "Tópico 1 Qualidade dos dados: comente a completude das informações (se há muitos campos "
    "sem dados, se a base é robusta). "
    "Tópico 2 Tendências identificadas: descreva padrões visíveis nas métricas (alta, queda, "
    "estabilidade). "
    "Tópico 3 Comparação temporal: compare o período atual com o anterior quando possível. "
    "Tópico 4 Pontos de atenção: destaque alertas ou indicadores preocupantes. "
    "Use somente os números e as fontes fornecidos e nunca invente dados. Escreva em "
    "português simples. Separe cada tópico com uma quebra de linha dupla. Não use travessões, "
    "dois-pontos nem ponto e vírgula."
)


def _fmt_metrica(m: Metrica) -> str:
    valor = "N/A" if m.valor is None else f"{m.valor}{m.unidade}"
    return f"- {m.nome}: {valor} (base de {m.denominador} pessoas avaliadas)"


def montar_prompt_avaliacao(
    metricas: list[Metrica],
    noticias: list[Noticia],
    narrativa: str,
    referencia: date | None,
) -> tuple[str, str]:
    """Retorna (system, user) para gerar a avaliação complementar."""
    linhas_m = "\n".join(_fmt_metrica(m) for m in metricas) or "(sem métricas)"
    linhas_n = "\n".join(f"- {n.titulo} ({n.fonte})" for n in noticias) or "(sem notícias)"
    user = (
        f"Período de referência: {referencia}.\n\n"
        f"Métricas (últimos 30 dias):\n{linhas_m}\n\n"
        f"Notícias recentes sobre SRAG:\n{linhas_n}\n\n"
        f"Narrativa gerada:\n{narrativa}"
    )
    return _SYSTEM_AVALIACAO, user

