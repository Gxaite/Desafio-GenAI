"""Testes das métricas (puras) e das tools (com repositório fake — sem banco)."""

from __future__ import annotations

from datetime import date

from srag_report.application.tools import (
    calcular_metricas,
    dados_grafico,
    mapa_uf,
    referencia_efetiva,
)
from srag_report.domain import metrics
from srag_report.domain.models import AgregadoSRAG, AgregadoUF, Periodo, PontoSerie

REF = date(2026, 7, 5)


def _agg(**kw: int) -> AgregadoSRAG:
    return AgregadoSRAG(**kw)


# ── métricas puras ──

def test_mortalidade() -> None:
    m = metrics.taxa_mortalidade(_agg(ev_cura=90, ev_obito=5, ev_obito_outras=5))
    assert m.valor == 5.0 and m.denominador == 100 and m.unidade == "%"


def test_uti_proxy() -> None:
    m = metrics.taxa_ocupacao_uti(_agg(uti_sim=25, uti_nao=75))
    assert m.valor == 25.0 and m.denominador == 100


def test_vacinacao_proxy() -> None:
    m = metrics.taxa_vacinacao(_agg(vac_sim=38, vac_nao=62))
    assert m.valor == 38.0


def test_aumento_positivo_e_negativo() -> None:
    assert metrics.taxa_aumento_casos(100, 80).valor == 25.0
    assert metrics.taxa_aumento_casos(60, 80).valor == -25.0


def test_denominador_zero_vira_none() -> None:
    # Sem casos com desfecho/UTI/vacina conhecidos → N/A, nunca divisão por zero.
    assert metrics.taxa_mortalidade(_agg()).valor is None
    assert metrics.taxa_ocupacao_uti(_agg()).valor is None
    assert metrics.taxa_aumento_casos(10, 0).valor is None


# ── tools (composição) com repositório fake ──

class _FakeRepo:
    def data_mais_recente(self) -> date | None:
        return REF

    def agregado(self, periodo: Periodo, uf: str | None = None) -> AgregadoSRAG:
        base = 100 if uf is None else 40  # UF filtra para menos casos
        # período "atual" termina em REF; o "anterior" termina antes.
        if periodo.fim == REF:
            return _agg(casos=base, ev_cura=90, ev_obito=5, ev_obito_outras=5,
                        uti_sim=25, uti_nao=75, vac_sim=38, vac_nao=62)
        return _agg(casos=80)

    def agregado_por_uf(self, periodo: Periodo) -> list[AgregadoUF]:
        return [
            AgregadoUF(uf="SP", uf_nome="São Paulo", regiao="Sudeste", casos=100,
                       mortalidade=5.0, uti=25.0, vacinacao=38.0),
            AgregadoUF(uf="RJ", uf_nome="Rio de Janeiro", regiao="Sudeste", casos=50,
                       mortalidade=None, uti=None, vacinacao=None),
        ]

    def serie_diaria(self, periodo: Periodo) -> list[PontoSerie]:
        return [PontoSerie(competencia=periodo.fim, casos=100)]

    def serie_mensal(self, periodo: Periodo) -> list[PontoSerie]:
        return [PontoSerie(competencia=periodo.inicio, casos=100)]


def test_calcular_metricas_retorna_as_quatro() -> None:
    ms = calcular_metricas(_FakeRepo())
    nomes = [m.nome for m in ms]
    assert nomes == [
        "Taxa de aumento de casos",
        "Taxa de mortalidade",
        "Taxa de ocupação de UTI",
        "Taxa de vacinação",
    ]
    assert ms[0].valor == 25.0  # (100-80)/80
    assert ms[1].valor == 5.0


def test_janela_12_meses_comeca_no_primeiro_dia() -> None:
    series = dados_grafico(_FakeRepo())
    # 12 meses inclusivos terminando em jul/2026 → começa em ago/2025.
    assert series.mensal_12m[0].competencia == date(2025, 8, 1)
    assert series.diaria_30d[0].competencia == REF


def test_calcular_metricas_filtra_por_uf() -> None:
    # sem UF usa o total (100); com UF o fake retorna menos casos (40).
    assert calcular_metricas(_FakeRepo())[0].denominador == 80
    ms_uf = calcular_metricas(_FakeRepo(), uf="SP")
    assert ms_uf[1].nome == "Taxa de mortalidade"  # a lista continua com as 4


def test_mapa_uf_retorna_ufs_com_taxas() -> None:
    ufs = mapa_uf(_FakeRepo(), dias=30)
    assert [u.uf for u in ufs] == ["SP", "RJ"]
    assert ufs[0].casos == 100 and ufs[0].uti == 25.0
    assert ufs[1].uti is None  # sem base conhecida vira None


def test_referencia_recua_dias_provisorios() -> None:
    # Sem referência explícita, recua os dias provisórios (atraso de notificação — adr-0017).
    assert referencia_efetiva(_FakeRepo(), None, 14) == date(2026, 6, 21)  # 05/07 - 14
    # Referência explícita é respeitada como está.
    assert referencia_efetiva(_FakeRepo(), date(2026, 1, 1), 14) == date(2026, 1, 1)
    # 0 = usa o último dia com dado.
    assert referencia_efetiva(_FakeRepo(), None, 0) == REF
