"""Tools de dados — orquestram repositório + domínio. Determinísticas e auditáveis.

São as ferramentas que o agente (Fase 4) invocará. Aqui, funções puras de composição:
recebem um `RepositorioDados` (port) e devolvem modelos tipados.
"""

from __future__ import annotations

from datetime import date, timedelta

from srag_report.domain import metrics
from srag_report.domain.errors import ErroDados
from srag_report.domain.models import AgregadoUF, Metrica, Noticia, Periodo, SeriesGraficos
from srag_report.domain.news import filtrar_relevantes
from srag_report.domain.ports import FonteNoticias, RepositorioDados

_JANELA_DIAS = 30


def referencia_efetiva(
    repo: RepositorioDados, referencia: date | None = None, dias_provisorios: int = 0
) -> date:
    """Referência de análise. Se explícita, usa-a; senão, recua `dias_provisorios` a partir do
    último dia com dado (exclui a cauda subnotificada por atraso de notificação — adr-0017)."""
    if referencia is not None:
        return referencia
    ref = repo.data_mais_recente()
    if ref is None:
        raise ErroDados("mart vazio: rode o ETL antes de calcular métricas")
    return ref - timedelta(days=dias_provisorios)


def calcular_metricas(
    repo: RepositorioDados, referencia: date | None = None, *,
    dias_provisorios: int = 0, uf: str | None = None,
) -> list[Metrica]:
    """As 4 métricas para os últimos 30 dias até a referência efetiva (default: último dia
    com dado, recuado por `dias_provisorios`). Filtra por `uf` quando informada."""
    ref = referencia_efetiva(repo, referencia, dias_provisorios)
    atual = Periodo(inicio=ref - timedelta(days=_JANELA_DIAS - 1), fim=ref)
    anterior = Periodo(
        inicio=ref - timedelta(days=2 * _JANELA_DIAS - 1),
        fim=ref - timedelta(days=_JANELA_DIAS),
    )
    a = repo.agregado(atual, uf)
    ant = repo.agregado(anterior, uf)
    return [
        metrics.taxa_aumento_casos(a.casos, ant.casos),
        metrics.taxa_mortalidade(a),
        metrics.taxa_ocupacao_uti(a),
        metrics.taxa_vacinacao(a),
    ]


def dados_grafico(
    repo: RepositorioDados, referencia: date | None = None, *, dias_provisorios: int = 0
) -> SeriesGraficos:
    """Séries dos 2 gráficos: casos diários (30 dias) e mensais (12 meses)."""
    ref = referencia_efetiva(repo, referencia, dias_provisorios)
    inicio_diaria = ref - timedelta(days=_JANELA_DIAS - 1)
    inicio_mensal = _inicio_12_meses(ref)
    return SeriesGraficos(
        diaria_30d=repo.serie_diaria(Periodo(inicio=inicio_diaria, fim=ref)),
        mensal_12m=repo.serie_mensal(Periodo(inicio=inicio_mensal, fim=ref)),
    )


def mapa_uf(
    repo: RepositorioDados, *, dias: int | None = 30, dias_provisorios: int = 0
) -> list[AgregadoUF]:
    """Casos e taxas por UF no período (para o mapa). `dias=None` usa todo o histórico."""
    ref = referencia_efetiva(repo, None, dias_provisorios)
    inicio = ref - timedelta(days=dias - 1) if dias else date(2000, 1, 1)
    return repo.agregado_por_uf(Periodo(inicio=inicio, fim=ref))


def _inicio_12_meses(ref: date) -> date:
    """1º dia do mês 11 meses antes do mês de `ref` (janela de 12 meses inclusiva)."""
    total = ref.year * 12 + (ref.month - 1) - 11
    ano, mes = divmod(total, 12)
    return date(ano, mes + 1, 1)


def buscar_noticias(
    fonte: FonteNoticias, consulta: str = "SRAG", *, limite: int = 5
) -> list[Noticia]:
    """Notícias da fonte, já filtradas por relevância (guardrail) ao tema SRAG."""
    return filtrar_relevantes(fonte.buscar(consulta, limite=limite))
