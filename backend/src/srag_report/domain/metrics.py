"""As 4 métricas de SRAG — funções puras e determinísticas sobre agregados.

O LLM nunca calcula: tudo aqui é Python puro, testável sem mocks
(vault/adr-0004-llm-orquestra-python-calcula). Denominadores usam apenas valores
conhecidos (1/2), nunca ignorados/ausentes — a premissa vira `observacao` (transparência).
"""

from __future__ import annotations

from srag_report.domain.models import AgregadoSRAG, Metrica


def _taxa(numerador: int, denominador: int) -> float | None:
    """Percentual arredondado; None quando não há denominador (evita divisão por zero)."""
    if denominador <= 0:
        return None
    return round(100.0 * numerador / denominador, 2)


def taxa_aumento_casos(casos_atual: int, casos_anterior: int) -> Metrica:
    """Variação % de casos entre o período atual e o anterior de mesma duração."""
    return Metrica(
        nome="Taxa de aumento de casos",
        valor=_taxa(casos_atual - casos_anterior, casos_anterior),
        unidade="%",
        denominador=casos_anterior,
        observacao="variação vs. período anterior de igual duração",
    )


def taxa_mortalidade(a: AgregadoSRAG) -> Metrica:
    """Óbitos por SRAG sobre casos com desfecho conhecido (cura/óbito/óbito outras)."""
    denominador = a.ev_cura + a.ev_obito + a.ev_obito_outras
    return Metrica(
        nome="Taxa de mortalidade",
        valor=_taxa(a.ev_obito, denominador),
        unidade="%",
        denominador=denominador,
        observacao="óbitos (EVOLUCAO=2) / casos com desfecho conhecido",
    )


def taxa_ocupacao_uti(a: AgregadoSRAG) -> Metrica:
    """Proxy: casos que foram à UTI sobre casos com status de UTI conhecido."""
    denominador = a.uti_sim + a.uti_nao
    return Metrica(
        nome="Taxa de ocupação de UTI",
        valor=_taxa(a.uti_sim, denominador),
        unidade="%",
        denominador=denominador,
        observacao="proxy: casos com UTI=sim / casos com UTI conhecida (não leitos)",
    )


def taxa_vacinacao(a: AgregadoSRAG) -> Metrica:
    """Proxy: casos vacinados (COVID) sobre casos com status de vacinação conhecido."""
    denominador = a.vac_sim + a.vac_nao
    return Metrica(
        nome="Taxa de vacinação",
        valor=_taxa(a.vac_sim, denominador),
        unidade="%",
        denominador=denominador,
        observacao="proxy: vacinados / casos com status conhecido (não cobertura populacional)",
    )
