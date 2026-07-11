"""Renderiza o relatório em PDF: HTML (Jinja2) → WeasyPrint.

O rodapé de transparência (modelo, fontes, run_id, timestamp) atende o critério de
governança/transparência (vault/qualidade-governanca.md).
"""

from __future__ import annotations

from typing import Any

from jinja2 import Template
from weasyprint import HTML

_TEMPLATE = Template(
    """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><style>
  @page { size: A4; margin: 1.8cm; }
  body { font-family: sans-serif; color: #1f2937; font-size: 12px; }
  h1 { font-size: 20px; margin: 0 0 2px; }
  .sub { color: #6b7280; font-size: 11px; margin-bottom: 16px; }
  .metricas { display: flex; gap: 10px; margin: 14px 0; }
  .card { flex: 1; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }
  .card .v { font-size: 20px; font-weight: 700; color: #111827; }
  .card .n { font-size: 15px; font-weight: 400; color:#6b7280; }
  .card .t { font-size: 10px; color: #6b7280; text-transform: uppercase; }
  .card .o { font-size: 9px; color: #9ca3af; margin-top: 4px; }
  h2 { font-size: 13px; margin: 18px 0 6px; border-bottom: 1px solid #e5e7eb; }
  img { width: 100%; }
  .narrativa { line-height: 1.5; text-align: justify; }
  ul { margin: 4px 0; padding-left: 18px; } li { margin: 2px 0; }
  .rodape { margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 8px;
            font-size: 9px; color: #9ca3af; }
</style></head><body>
  <h1>Relatório de SRAG</h1>
  <div class="sub">Período de referência: {{ referencia }} · últimos 30 dias</div>

  <div class="metricas">
  {% for m in metricas %}
    <div class="card">
      <div class="t">{{ m.nome }}</div>
      <div class="v">{% if m.valor is none %}N/A{% else %}{{ m.valor }}{{ m.unidade }}{% endif %}
        <span class="n">(N={{ m.denominador }})</span></div>
      <div class="o">{{ m.observacao }}</div>
    </div>
  {% endfor %}
  </div>

  <h2>Análise</h2>
  <div class="narrativa">{{ narrativa }}</div>

  <h2>Casos diários — últimos 30 dias</h2>
  <img src="{{ grafico_diario }}">
  <h2>Casos mensais — últimos 12 meses</h2>
  <img src="{{ grafico_mensal }}">

  <h2>Notícias consideradas</h2>
  {% if noticias %}<ul>
    {% for n in noticias %}<li>{{ n.titulo }} — <i>{{ n.fonte }}</i></li>{% endfor %}
  </ul>{% else %}<p>Nenhuma notícia relevante disponível nesta execução.</p>{% endif %}

  <div class="rodape">
    Gerado em {{ gerado_em }} · modelo: {{ modelo }} · run_id: {{ run_id }}<br>
    Fonte de dados: Open DATASUS (SIVEP-Gripe). Métricas de UTI e vacinação são proxies
    (status por caso). Números calculados deterministicamente; narrativa gerada por LLM
    sobre esses números.
  </div>
</body></html>"""
)


def renderar_pdf(contexto: dict[str, Any]) -> bytes:
    html = _TEMPLATE.render(**contexto)
    return HTML(string=html).write_pdf()  # type: ignore[no-any-return]
