"""Tools de dados — orquestram repositório + domínio. Determinísticas e auditáveis.

São as ferramentas que o agente (Fase 4) invocará. Aqui, funções puras de composição:
recebem um `RepositorioDados` (port) e devolvem modelos tipados.
"""

from __future__ import annotations

from datetime import date, timedelta

from srag_report.domain import metrics
from srag_report.domain.errors import ErroDados
from srag_report.domain.models import Metrica, Periodo, SeriesGraficos
from srag_report.domain.ports import RepositorioDados

_JANELA_DIAS = 30


def _referencia(repo: RepositorioDados, referencia: date | None) -> date:
    ref = referencia or repo.data_mais_recente()
    if ref is None:
        raise ErroDados("mart vazio: rode o ETL antes de calcular métricas")
    return ref


def calcular_metricas(repo: RepositorioDados, referencia: date | None = None) -> list[Metrica]:
    """As 4 métricas para os últimos 30 dias até `referencia` (default: dado mais recente)."""
    ref = _referencia(repo, referencia)
    atual = Periodo(inicio=ref - timedelta(days=_JANELA_DIAS - 1), fim=ref)
    anterior = Periodo(
        inicio=ref - timedelta(days=2 * _JANELA_DIAS - 1),
        fim=ref - timedelta(days=_JANELA_DIAS),
    )
    a = repo.agregado(atual)
    ant = repo.agregado(anterior)
    return [
        metrics.taxa_aumento_casos(a.casos, ant.casos),
        metrics.taxa_mortalidade(a),
        metrics.taxa_ocupacao_uti(a),
        metrics.taxa_vacinacao(a),
    ]


def dados_grafico(repo: RepositorioDados, referencia: date | None = None) -> SeriesGraficos:
    """Séries dos 2 gráficos: casos diários (30 dias) e mensais (12 meses)."""
    ref = _referencia(repo, referencia)
    inicio_diaria = ref - timedelta(days=_JANELA_DIAS - 1)
    inicio_mensal = _inicio_12_meses(ref)
    return SeriesGraficos(
        diaria_30d=repo.serie_diaria(Periodo(inicio=inicio_diaria, fim=ref)),
        mensal_12m=repo.serie_mensal(Periodo(inicio=inicio_mensal, fim=ref)),
    )


def _inicio_12_meses(ref: date) -> date:
    """1º dia do mês 11 meses antes do mês de `ref` (janela de 12 meses inclusiva)."""
    total = ref.year * 12 + (ref.month - 1) - 11
    ano, mes = divmod(total, 12)
    return date(ano, mes + 1, 1)
