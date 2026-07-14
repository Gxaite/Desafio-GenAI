"""Gera o diagrama conceitual da arquitetura da solução.

Reproduzível e offline: SVG desenhado à mão → PDF via WeasyPrint (entregável) e
PNG via CairoSVG (usado no README, pois o GitHub renderiza imagem estática de forma
confiável). Mostra o Agente Principal (Orquestrador), as Tools, o LLM, o banco de
dados e a fonte de notícias, conforme o desafio.

Layout vertical (de cima para baixo), centralizado, com as caixas dimensionadas e a
fonte auto-ajustada para o texto nunca estourar as bordas.

Saídas:  docs/diagrama-conceitual.pdf  e  docs/assets/arquitetura.png

Uso:  uv run --with weasyprint --with cairosvg python docs/gerar_diagrama.py
"""

from __future__ import annotations

from pathlib import Path

from weasyprint import HTML

# Retrato: mais alto que largo, para o fluxo vertical respirar.
W, H = 900, 960
CX = W / 2  # eixo central do diagrama

AZUL, ROXO, AMBAR, VERDE, SLATE = "#2563eb", "#7c3aed", "#d97706", "#059669", "#475569"
TINTA, SUAVE = "#0f172a", "#475569"


def _fonte(texto: str, base: float, largura_util: float, fator: float) -> float:
    """Reduz a fonte só o necessário para o texto caber em `largura_util`."""
    est = len(texto) * base * fator
    if est <= largura_util:
        return base
    return max(7.5, largura_util / (len(texto) * fator))


def caixa(
    cx: float, y: float, w: float, h: float, titulo: str, sub: str,
    fill: str, stroke: str, tbase: float = 14.5,
) -> str:
    """Caixa arredondada centrada em `cx`, com título e subtítulo que se ajustam à largura."""
    x = cx - w / 2
    util = w - 26
    tf = _fonte(titulo, tbase, util, 0.62)
    ty = (y + h / 2 - 5) if sub else (y + h / 2 + tf * 0.35)
    svg = (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="10" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="1.8"/>'
        f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="{tf:.1f}" '
        f'font-weight="700" fill="{TINTA}">{titulo}</text>'
    )
    if sub:
        sf = _fonte(sub, 10.5, util, 0.55)
        svg += (
            f'<text x="{cx:.1f}" y="{y + h / 2 + 13:.1f}" text-anchor="middle" '
            f'font-size="{sf:.1f}" fill="{SUAVE}">{sub}</text>'
        )
    return svg


def seta(x1: float, y1: float, x2: float, y2: float, label: str = "") -> str:
    """Seta com ponta; label opcional numa pílula branca ao lado da linha (sem colidir)."""
    svg = (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{SLATE}" '
        f'stroke-width="1.8" marker-end="url(#a)"/>'
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        pw = len(label) * 6.4 + 14
        if abs(x2 - x1) < abs(y2 - y1):  # seta vertical -> pílula à direita
            lx, ly = mx + pw / 2 + 10, my
        else:  # seta horizontal -> pílula acima
            lx, ly = mx, my - 13
        svg += (
            f'<rect x="{lx - pw / 2:.1f}" y="{ly - 9:.1f}" width="{pw:.1f}" height="18" rx="5" '
            f'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
            f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" font-size="10" '
            f'fill="#334155">{label}</text>'
        )
    return svg


# ── Geometria do fluxo vertical ────────────────────────────────────────────────
SB = 290          # largura das caixas da espinha central
AG_X, AG_W = CX - 155, 310   # container do agente (305..615)
STEP_W = 270      # largura dos passos internos do agente

y_csv, y_etl, y_pg = 104, 202, 300
h_row = 64
ag_top = y_pg + h_row + 44          # 408
step_y = [ag_top + 46 + i * 70 for i in range(4)]  # 454, 524, 594, 664
step_h = 56
ag_bottom = step_y[-1] + step_h + 20
y_rel = ag_bottom + 42
y_band = y_rel + h_row + 30

partes = [
    # ── espinha: fonte -> ETL -> banco ──
    caixa(CX, y_csv, SB, h_row, "Open DATASUS", "SIVEP-Gripe (CSV, fonte oficial)", "#dbeafe", AZUL),
    caixa(CX, y_etl, SB, h_row, "ETL medallion (dbt)", "bronze · silver · gold", "#dbeafe", AZUL),
    caixa(CX, y_pg, SB, h_row, "Postgres · camada gold", "banco servido (fato + dimensões)", "#bfdbfe", "#1d4ed8"),
    # ── Grafana: saída à esquerda, alimentada pela gold ──
    caixa(172, y_pg, 200, h_row, "Grafana", "dashboard (bônus)", "#d1fae5", VERDE),
    # ── container do agente ──
    f'<rect x="{AG_X:.1f}" y="{ag_top}" width="{AG_W}" height="{ag_bottom - ag_top}" rx="14" '
    f'fill="#faf5ff" stroke="{ROXO}" stroke-width="2"/>',
    f'<text x="{CX:.1f}" y="{ag_top + 26}" text-anchor="middle" font-size="13.5" '
    f'font-weight="800" fill="{ROXO}">Agente Orquestrador · LangGraph</text>',
    # ── passos do agente (cada um aciona uma tool) ──
    caixa(CX, step_y[0], STEP_W, step_h, "1 · calcular_metricas", "consulta a gold", "#ede9fe", ROXO, 13.5),
    caixa(CX, step_y[1], STEP_W, step_h, "2 · dados_grafico", "séries a partir da gold", "#ede9fe", ROXO, 13.5),
    caixa(CX, step_y[2], STEP_W, step_h, "3 · buscar_noticias", "via NewsAPI", "#ede9fe", ROXO, 13.5),
    caixa(CX, step_y[3], STEP_W, step_h, "4 · narrativa", "LLM ancorado nos dados", "#ede9fe", ROXO, 13.5),
    # ── serviços externos à direita ──
    caixa(762, step_y[2], 215, step_h, "NewsAPI", "notícias em tempo real", "#fef3c7", AMBAR),
    caixa(762, step_y[3], 215, step_h, "OpenRouter · Claude", "LLM da narrativa", "#fef3c7", AMBAR),
    # ── saída ──
    caixa(CX, y_rel, SB, h_row, "Relatório PDF", "4 métricas · 2 gráficos · narrativa", "#d1fae5", VERDE),
    # ── faixa transversal ──
    f'<rect x="40" y="{y_band}" width="{W - 80}" height="46" rx="9" fill="#e2e8f0" '
    f'stroke="{SLATE}" stroke-width="1.4"/>',
    f'<text x="{CX:.1f}" y="{y_band + 28}" text-anchor="middle" font-size="11" fill="#334155">'
    'Transversais · Auditoria e governança (run_id) · Guardrails (grounding, validação, filtro) '
    '· Observabilidade (structlog)</text>',
    # ── setas do fluxo ──
    seta(CX, y_csv + h_row, CX, y_etl),                       # fonte -> ETL
    seta(CX, y_etl + h_row, CX, y_pg),                        # ETL -> banco
    seta(CX - SB / 2, y_pg + h_row / 2, 172 + 100, y_pg + h_row / 2),  # gold -> Grafana
    seta(CX, y_pg + h_row, CX, ag_top, "gold (SQL)"),         # gold -> agente
    seta(CX, step_y[0] + step_h, CX, step_y[1]),              # passo 1 -> 2
    seta(CX, step_y[1] + step_h, CX, step_y[2]),              # passo 2 -> 3
    seta(CX, step_y[2] + step_h, CX, step_y[3]),              # passo 3 -> 4
    seta(AG_X + AG_W, step_y[2] + step_h / 2, 762 - 215 / 2, step_y[2] + step_h / 2, "REST"),  # -> NewsAPI
    seta(AG_X + AG_W, step_y[3] + step_h / 2, 762 - 215 / 2, step_y[3] + step_h / 2, "chat"),  # -> Claude
    seta(CX, ag_bottom, CX, y_rel, "montar"),                 # agente -> relatório
]

svg = (
    f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
    'font-family="DejaVu Sans, sans-serif">'
    '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="4" '
    f'orient="auto"><path d="M0,0 L9,4 L0,8 z" fill="{SLATE}"/></marker></defs>'
    f'<text x="{CX:.1f}" y="46" text-anchor="middle" font-size="21" font-weight="800" '
    f'fill="{TINTA}">Arquitetura Conceitual — Relatório Automatizado de SRAG</text>'
    f'<text x="{CX:.1f}" y="72" text-anchor="middle" font-size="11.5" fill="{SUAVE}">'
    'o LLM orquestra e explica; o Python calcula (núcleo hexagonal, dados em medallion)</text>'
    + "".join(partes)
    + "</svg>"
)

html = f'<html><head><meta charset="utf-8"><style>@page {{ size: A4 portrait; margin: 1cm; }} '
html += f'body {{ margin: 0; }} svg {{ width: 100%; }}</style></head><body>{svg}</body></html>'

base = Path(__file__).resolve().parent

destino_pdf = base / "diagrama-conceitual.pdf"
HTML(string=html).write_pdf(str(destino_pdf))
print("gerado:", destino_pdf)

# PNG usado no README (2x para nitidez; fundo branco para ficar legível nos temas
# claro e escuro do GitHub, já que o texto do diagrama é escuro).
import cairosvg  # noqa: PLC0415  (dependência opcional, só para o PNG)

destino_png = base / "assets" / "arquitetura.png"
cairosvg.svg2png(
    bytestring=svg.encode("utf-8"),
    write_to=str(destino_png),
    output_width=2 * W,
    output_height=2 * H,
    background_color="white",
)
print("gerado:", destino_png)
