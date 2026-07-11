"""Modelos de domínio (pydantic) — schemas tipados de entrada/saída das tools.

Puros: sem I/O, sem frameworks além do pydantic (validação = guardrail).
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class Periodo(BaseModel):
    """Intervalo fechado [inicio, fim]."""

    inicio: date
    fim: date


class AgregadoSRAG(BaseModel):
    """Contagens agregadas de um período (soma do mart gold). Sem indivíduos."""

    casos: int = 0
    ev_cura: int = 0
    ev_obito: int = 0
    ev_obito_outras: int = 0
    uti_sim: int = 0
    uti_nao: int = 0
    vac_sim: int = 0
    vac_nao: int = 0


class Metrica(BaseModel):
    """Uma métrica calculada — valor + metadados de transparência."""

    nome: str
    valor: float | None = Field(description="None quando não há denominador (N/A).")
    unidade: str
    denominador: int = Field(description="N usado no cálculo (transparência).")
    observacao: str | None = None


class PontoSerie(BaseModel):
    """Um ponto de série temporal (dia ou mês)."""

    competencia: date
    casos: int


class SeriesGraficos(BaseModel):
    """As duas séries exigidas no relatório."""

    diaria_30d: list[PontoSerie]
    mensal_12m: list[PontoSerie]


class Noticia(BaseModel):
    """Uma notícia retornada pela fonte externa (após filtro de relevância)."""

    titulo: str
    fonte: str
    url: str
    publicado_em: date | None = None
    descricao: str | None = None


class EventoAuditoria(BaseModel):
    """Um evento da trilha de auditoria do agente (uma linha por passo)."""

    no: str
    tipo: str  # tool | llm | fallback | decisao
    detalhe: str
    ts: datetime


class DadosRelatorio(BaseModel):
    """Tudo que o relatório precisa — o renderizador (adapter) transforma isto em PDF."""

    referencia: date | None
    metricas: list[Metrica]
    series: SeriesGraficos
    noticias: list[Noticia]
    narrativa: str
    run_id: str
    modelo: str
    gerado_em: str
