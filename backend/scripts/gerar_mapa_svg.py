"""Gera src/srag_report/api/mapa_svg.py a partir de uma malha pública dos estados do Brasil.

Usa uma malha validada (codeforgermany/click_that_hood, baseada no IBGE), projeta lon/lat em
coordenadas SVG (equiretangular), simplifica (arredonda, descarta pontos muito próximos e ilhas
pequenas) e emite um path por UF (id = sigla). Só Python puro, sem dependência geoespacial.

Uso:
    curl -sSL -o /tmp/br.geojson \\
      https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/brazil-states.geojson
    python scripts/gerar_mapa_svg.py /tmp/br.geojson
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_NOME_UF = {
    "Acre": "AC", "Alagoas": "AL", "Amazonas": "AM", "Amapá": "AP", "Bahia": "BA", "Ceará": "CE",
    "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA", "Minas Gerais": "MG",
    "Mato Grosso do Sul": "MS", "Mato Grosso": "MT", "Pará": "PA", "Paraíba": "PB",
    "Pernambuco": "PE", "Piauí": "PI", "Paraná": "PR", "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN", "Rondônia": "RO", "Roraima": "RR", "Rio Grande do Sul": "RS",
    "Santa Catarina": "SC", "Sergipe": "SE", "São Paulo": "SP", "Tocantins": "TO",
    "Distrito Federal": "DF",
}
_W = 100.0
_MIN_D = 0.55   # distância mínima entre pontos (decimação)
_AREA_MIN = 0.06  # área mínima de anel (descarta ilhas pequenas), em graus²


def _area(ring: list) -> float:
    a = 0.0
    for i in range(len(ring) - 1):
        a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
    return abs(a) / 2


def main() -> None:
    origem = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/br.geojson")
    dados = json.loads(origem.read_text())
    pts_lon = [x for f in dados["features"] for poly in f["geometry"]["coordinates"]
               for ring in poly for x, _ in ring]
    pts_lat = [y for f in dados["features"] for poly in f["geometry"]["coordinates"]
               for ring in poly for _, y in ring]
    lon_min, lon_max = min(pts_lon), max(pts_lon)
    lat_min, lat_max = min(pts_lat), max(pts_lat)
    sx = _W / (lon_max - lon_min)
    altura = round((lat_max - lat_min) * sx, 1)

    def caminho(ring: list) -> str:
        pts, ult = [], None
        for x, y in ring:
            px, py = (x - lon_min) * sx, (lat_max - y) * sx
            if ult is None or (px - ult[0]) ** 2 + (py - ult[1]) ** 2 >= _MIN_D * _MIN_D:
                pts.append((round(px, 1), round(py, 1)))
                ult = (px, py)
        return "M" + "L".join(f"{a},{b}" for a, b in pts) + "Z" if len(pts) >= 3 else ""

    linhas = []
    for f in sorted(dados["features"], key=lambda f: f["properties"]["name"]):
        uf = _NOME_UF[f["properties"]["name"]]
        partes = [caminho(poly[0]) for poly in f["geometry"]["coordinates"]
                  if _area(poly[0]) >= _AREA_MIN]
        linhas.append(f'<path id="{uf}" d="{"".join(p for p in partes if p)}"/>')

    destino = Path(__file__).resolve().parent.parent / "src/srag_report/api/mapa_svg.py"
    corpo = "".join("    " + repr(x) + "\n" for x in linhas)
    destino.write_text(
        '"""Malha dos estados do Brasil como paths SVG (id = sigla da UF).\n\n'
        "Gerada por scripts/gerar_mapa_svg.py a partir de uma malha pública validada "
        "(codeforgermany/click_that_hood, baseada no IBGE), simplificada. Sem dependência "
        'geoespacial em runtime.\n"""\n\n# ruff: noqa: E501\nfrom __future__ import annotations\n\n'
        f'VIEWBOX = "0 0 100 {altura}"\n\nESTADOS_SVG = (\n{corpo})\n'
    )
    print(f"escrito {destino} ({len(linhas)} estados, viewBox 0 0 100 {altura})")


if __name__ == "__main__":
    main()
