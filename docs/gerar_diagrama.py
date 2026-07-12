"""Gera docs/diagrama-conceitual.pdf — diagrama conceitual da arquitetura da solução.

Reproduzível e offline: SVG desenhado à mão → PDF via WeasyPrint. Mostra o Agente Principal
(Orquestrador), as Tools, o LLM, o banco de dados e a fonte de notícias, conforme o desafio.

Uso:  uv run --with weasyprint python docs/gerar_diagrama.py
"""

from __future__ import annotations

from pathlib import Path

from weasyprint import HTML

W, H = 1000, 560


def caixa(x: int, y: int, w: int, h: int, titulo: str, sub: str, fill: str, stroke: str) -> str:
    ty = y + h / 2 + (0 if not sub else -5)
    svg = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="1.6"/>'
        f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" font-size="13" '
        f'font-weight="700" fill="#0f172a">{titulo}</text>'
    )
    if sub:
        svg += (
            f'<text x="{x + w / 2}" y="{y + h / 2 + 12}" text-anchor="middle" '
            f'font-size="9.5" fill="#475569">{sub}</text>'
        )
    return svg


def seta(x1: int, y1: int, x2: int, y2: int, label: str = "") -> str:
    svg = (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#64748b" '
        f'stroke-width="1.6" marker-end="url(#a)"/>'
    )
    if label:
        svg += (
            f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 4}" text-anchor="middle" '
            f'font-size="9" fill="#334155">{label}</text>'
        )
    return svg


AZUL, ROXO, AMBAR, VERDE, SLATE = "#2563eb", "#7c3aed", "#d97706", "#059669", "#475569"

partes = [
    # container do agente
    f'<rect x="278" y="82" width="322" height="342" rx="12" fill="#faf5ff" '
    f'stroke="{ROXO}" stroke-width="2"/>',
    f'<text x="439" y="106" text-anchor="middle" font-size="13.5" font-weight="800" '
    f'fill="{ROXO}">Agente Principal (Orquestrador) · LangGraph</text>',
    # ── coluna de dados / ETL ──
    caixa(40, 92, 170, 48, "CSV Open DATASUS", "SIVEP-Gripe (2025+2026)", "#dbeafe", AZUL),
    caixa(40, 170, 170, 44, "ETL medallion (dbt)", "bronze -> silver -> gold", "#dbeafe", AZUL),
    caixa(40, 242, 170, 56, "Postgres · camada gold", "Banco de dados (fato + dims)", "#bfdbfe", "#1d4ed8"),
    caixa(40, 330, 170, 44, "Grafana", "dashboard (bonus)", "#d1fae5", VERDE),
    # ── nós do agente (cada um chama uma tool) ──
    caixa(300, 122, 200, 46, "1 · calcular_metricas", "tool -> gold", "#ede9fe", ROXO),
    caixa(300, 184, 200, 46, "2 · dados_grafico", "tool -> gold", "#ede9fe", ROXO),
    caixa(300, 246, 200, 46, "3 · buscar_noticias", "tool -> NewsAPI", "#ede9fe", ROXO),
    caixa(300, 308, 200, 46, "4 · narrativa", "no -> LLM", "#ede9fe", ROXO),
    # ── externos ──
    caixa(672, 246, 180, 46, "NewsAPI", "fonte de noticias (tempo real)", "#fef3c7", AMBAR),
    caixa(672, 308, 180, 46, "OpenRouter · Claude", "LLM (narrativa)", "#fef3c7", AMBAR),
    # ── saída ──
    caixa(300, 442, 200, 50, "Relatorio PDF", "4 metricas · 2 graficos · narrativa", "#d1fae5", VERDE),
    # ── faixa transversal ──
    f'<rect x="300" y="506" width="552" height="38" rx="8" fill="#e2e8f0" stroke="{SLATE}" stroke-width="1.4"/>',
    '<text x="576" y="530" text-anchor="middle" font-size="10.5" fill="#334155">'
    'Transversais: Auditoria &amp; Governanca (run_id) · Guardrails (grounding/validacao/filtro) '
    '· Observabilidade (structlog)</text>',
    # ── setas ──
    seta(125, 140, 125, 170),          # CSV -> ETL
    seta(125, 214, 125, 242),          # ETL -> gold
    seta(125, 298, 125, 330),          # gold -> Grafana
    seta(210, 262, 300, 145, "SQL"),   # gold -> calcular_metricas
    seta(210, 275, 300, 207),          # gold -> dados_grafico
    seta(400, 168, 400, 184),          # no1 -> no2
    seta(400, 230, 400, 246),          # no2 -> no3
    seta(400, 292, 400, 308),          # no3 -> no4
    seta(500, 269, 672, 269, "REST"),  # buscar_noticias -> NewsAPI
    seta(500, 331, 672, 331, "chat"),  # narrativa -> LLM
    seta(420, 424, 400, 442, "montar"),  # agente -> Relatorio
]

svg = (
    f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
    f'font-family="DejaVu Sans, sans-serif">'
    '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="4" '
    'orient="auto"><path d="M0,0 L9,4 L0,8 z" fill="#64748b"/></marker></defs>'
    f'<text x="{W / 2}" y="42" text-anchor="middle" font-size="19" font-weight="800" '
    'fill="#0f172a">Arquitetura Conceitual — Relatorio Automatizado de SRAG</text>'
    f'<text x="{W / 2}" y="62" text-anchor="middle" font-size="11" fill="#64748b">'
    'o LLM orquestra e explica; o Python calcula (nucleo hexagonal, dados em medallion)</text>'
    + "".join(partes)
    + "</svg>"
)

html = f'<html><head><meta charset="utf-8"><style>@page {{ size: A4 landscape; margin: 1cm; }} '
html += f'body {{ margin: 0; }} svg {{ width: 100%; }}</style></head><body>{svg}</body></html>'

destino = Path(__file__).resolve().parent / "diagrama-conceitual.pdf"
HTML(string=html).write_pdf(str(destino))
print("gerado:", destino)
