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
  @page { size: A4; margin: 1.6cm; }
  body { font-family: sans-serif; color: #0f172a; font-size: 12px; line-height: 1.5; }
  .head { display: flex; justify-content: space-between; align-items: baseline;
          border-bottom: 2px solid #0f172a; padding-bottom: 8px; }
  h1 { font-size: 21px; margin: 0; letter-spacing: -.02em; }
  .per { color: #64748b; font-size: 11px; }
  .kpis { display: flex; gap: 10px; margin: 16px 0 8px; }
  .kpi { flex: 1; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; }
  .kpi .t { font-size: 9.5px; color: #64748b; text-transform: uppercase; letter-spacing: .03em; }
  .kpi .v { font-size: 25px; font-weight: 800; color: #0f172a; margin-top: 3px;
            font-variant-numeric: tabular-nums; }
  .kpi .n { font-size: 11px; font-weight: 500; color: #94a3b8; }
  .kpi .o { font-size: 9px; color: #94a3b8; margin-top: 6px; line-height: 1.3; }
  .lab { font-size: 11px; font-weight: 700; color: #334155; text-transform: uppercase;
         letter-spacing: .04em; margin: 18px 0 6px; }
  img { width: 100%; }
  .leitura { border-left: 3px solid #0f172a; padding: 2px 0 2px 12px; color: #1f2937; }
  .fontes { font-size: 10.5px; color: #475569; }
  .fontes .f { color: #94a3b8; }
  .rodape { margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 8px;
            font-size: 9px; color: #94a3b8; }
</style></head><body>
  <div class="head">
    <h1>Relatório de SRAG</h1>
    <span class="per">Últimos 30 dias · referência {{ referencia }}</span>
  </div>

  <div class="kpis">
  {% for m in metricas %}
    <div class="kpi">
      <div class="t">{{ m.nome }}</div>
      <div class="v">{% if m.valor is none %}N/A{% else %}{{ m.valor }}{{ m.unidade }}{% endif %}</div>
      <div class="n">N = {{ m.denominador }}</div>
      <div class="o">{{ m.observacao }}</div>
    </div>
  {% endfor %}
  </div>

  <img src="{{ grafico_diario }}">
  <img src="{{ grafico_mensal }}">

  <div class="lab">Leitura do período</div>
  <div class="leitura">{{ narrativa }}</div>

  <div class="lab">Fontes consultadas</div>
  {% if noticias %}<div class="fontes">
    {% for n in noticias %}{{ n.titulo }} <span class="f">({{ n.fonte }})</span><br>{% endfor %}
  </div>{% else %}<div class="fontes">Nenhuma notícia relevante nesta execução.</div>{% endif %}

  <div class="rodape">
    Gerado em {{ gerado_em }} · modelo {{ modelo }} · run {{ run_id }}.
    Fonte: Open DATASUS (SIVEP-Gripe). UTI e vacinação são proxies por caso. Números
    calculados deterministicamente; narrativa escrita pelo LLM sobre esses números.
  </div>
</body></html>"""
)


def renderar_pdf(contexto: dict[str, Any]) -> bytes:
    html = _TEMPLATE.render(**contexto)
    return HTML(string=html).write_pdf()  # type: ignore[no-any-return]
