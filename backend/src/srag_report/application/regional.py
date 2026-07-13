"""Análise regional de uma UF. Overview textual gerado pelo LLM sobre as métricas daquela UF
e as notícias do período. Mesmo grounding do relatório nacional (o LLM só descreve os números
fornecidos), em linguagem acessível para leitores não técnicos.
"""

from __future__ import annotations

from datetime import timedelta

from srag_report.application.narrativa import validar_narrativa
from srag_report.application.tools import (
    buscar_noticias,
    calcular_metricas,
    referencia_efetiva,
)
from srag_report.domain.errors import ErroFonteNoticias
from srag_report.domain.models import AnaliseRegional, Metrica
from srag_report.domain.news import filtrar_relevantes
from srag_report.domain.ports import (
    FonteNoticias,
    ModeloLLM,
    RepositorioDados,
    RepositorioNoticias,
)

_SYSTEM = (
    "Você é um analista de saúde pública escrevendo para gestores e leitores não técnicos de uma "
    "região específica. Escreva de 2 a 4 frases claras, em português simples, com um panorama da "
    "SRAG na região indicada, usando somente os números e as notícias fornecidos e nunca "
    "inventando dados. Dê destaque ao indicador em foco quando houver. Trate as taxas como "
    "percentuais entre as pessoas avaliadas e não como cobertura da população. Não use "
    "títulos, listas nem markdown, apenas frases corridas. Não use travessões, dois-pontos "
    "nem ponto e vírgula."
)


def _fmt(m: Metrica) -> str:
    valor = "sem dados" if m.valor is None else f"{m.valor}{m.unidade}"
    return f"- {m.nome}: {valor} (base de {m.denominador} pessoas avaliadas)"


def analise_regional(
    repo: RepositorioDados,
    fonte: FonteNoticias,
    llm: ModeloLLM,
    uf: str,
    uf_nome: str,
    *,
    foco: str = "",
    dias_provisorios: int = 0,
    noticias_repo: RepositorioNoticias | None = None,
) -> AnaliseRegional:
    """Overview regional de uma UF. Se a NewsAPI falhar (ex.: 429), usa o histórico do banco."""
    ref = referencia_efetiva(repo, None, dias_provisorios)
    metricas = calcular_metricas(repo, ref, uf=uf)
    try:
        noticias = buscar_noticias(fonte, f"SRAG {uf_nome}", limite=8) or buscar_noticias(
            fonte, "SRAG", limite=6
        )
    except ErroFonteNoticias:
        if noticias_repo is None:
            raise
        desde = (ref - timedelta(days=30)) if ref else None
        noticias = filtrar_relevantes(noticias_repo.listar(limite=8, desde=desde))
    linhas_m = "\n".join(_fmt(m) for m in metricas)
    linhas_n = "\n".join(f"- {n.titulo} ({n.fonte})" for n in noticias) or "(sem notícias)"
    foco_txt = f" Indicador em foco {foco}." if foco else ""
    user = (
        f"Região {uf_nome}. Período últimos 30 dias até {ref}.{foco_txt}\n\n"
        f"Métricas da região\n{linhas_m}\n\nNotícias recentes\n{linhas_n}"
    )
    overview = validar_narrativa(llm.completar(_SYSTEM, user))
    return AnaliseRegional(
        uf=uf, uf_nome=uf_nome, referencia=ref, metricas=metricas, overview=overview
    )
