"""Ports (interfaces) do domínio — implementadas por adapters na infraestrutura.

O domínio depende destas abstrações, nunca de SDKs concretos (DIP).
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from srag_report.domain.models import (
    AgregadoSRAG,
    DadosRelatorio,
    EventoAuditoria,
    ExecucaoAgente,
    Metrica,
    Noticia,
    Periodo,
    PontoSerie,
    ResumoExecucao,
)


class RepositorioDados(Protocol):
    """Acesso de leitura aos marts agregados (camada gold)."""

    def data_mais_recente(self) -> date | None:
        """Data do registro mais recente no mart (âncora dos períodos)."""
        ...

    def agregado(self, periodo: Periodo) -> AgregadoSRAG:
        """Soma das contagens no período (nacional)."""
        ...

    def serie_diaria(self, periodo: Periodo) -> list[PontoSerie]:
        """Casos por dia no período."""
        ...

    def serie_mensal(self, periodo: Periodo) -> list[PontoSerie]:
        """Casos por mês no período."""
        ...


class FonteNoticias(Protocol):
    """Fonte externa de notícias (ex.: NewsAPI)."""

    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        """Notícias mais recentes para a consulta. Pode retornar [] (degradação)."""
        ...


class ModeloLLM(Protocol):
    """LLM que gera a narrativa. Recebe prompts prontos (grounding é do chamador)."""

    def completar(self, system: str, user: str) -> str:
        """Gera texto a partir de um prompt system+user. Levanta ErroModeloLLM em falha."""
        ...


class RepositorioAuditoria(Protocol):
    """Persiste e lê a trilha de auditoria de cada execução do agente (governança)."""

    def registrar(
        self,
        run_id: str,
        referencia: date | None,
        eventos: list[EventoAuditoria],
        metricas: list[Metrica],
        noticias: list[Noticia],
    ) -> None:
        """Grava a execução (trilha + métricas + fontes). Não derruba o relatório se falhar."""
        ...

    def listar_execucoes(self, limite: int = 20) -> list[ResumoExecucao]:
        """Execuções mais recentes (resumo)."""
        ...

    def obter_execucao(self, run_id: str) -> ExecucaoAgente | None:
        """Detalhe completo de uma execução (trilha + métricas + fontes)."""
        ...


class RenderizadorRelatorio(Protocol):
    """Transforma os dados do relatório no artefato final (ex.: PDF)."""

    def renderizar(self, dados: DadosRelatorio) -> bytes:
        ...
