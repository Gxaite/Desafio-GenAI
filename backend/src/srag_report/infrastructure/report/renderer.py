"""Adapter de RenderizadorRelatorio — orquestra gráficos (Plotly) + PDF (WeasyPrint).

É o único ponto que conhece as libs de render; a aplicação depende só do port.
"""

from __future__ import annotations

from srag_report.domain.models import DadosRelatorio
from srag_report.infrastructure.report.charts import graficos_data_uri
from srag_report.infrastructure.report.pdf_renderer import renderar_pdf


class RelatorioPdfRenderer:
    """Implementa `RenderizadorRelatorio` gerando um PDF."""

    def renderizar(self, dados: DadosRelatorio) -> bytes:
        grafico_diario, grafico_mensal = graficos_data_uri(dados.series)
        contexto = {
            "referencia": dados.referencia,
            "metricas": dados.metricas,
            "narrativa": dados.narrativa,
            "noticias": dados.noticias,
            "grafico_diario": grafico_diario,
            "grafico_mensal": grafico_mensal,
            "run_id": dados.run_id,
            "modelo": dados.modelo,
            "gerado_em": dados.gerado_em,
        }
        return renderar_pdf(contexto)
