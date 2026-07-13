"""Gera os README.md de cada camada (bronze/silver/gold) a partir dos artefatos do dbt.

Fonte da verdade: os arquivos `.yml` do projeto → `dbt` compila em `target/manifest.json`
(descrições) e `target/catalog.json` (tipos reais do banco). Este script apenas lê esses
artefatos e escreve os README, então a documentação por pasta fica sempre em sincronia com o
dbt, sem edição manual.

Uso:
    cd dados/dbt
    dbt docs generate          # gera manifest.json + catalog.json (introspecta o Postgres)
    python scripts/gerar_readmes.py
"""

from __future__ import annotations

import json
from pathlib import Path

_AQUI = Path(__file__).resolve().parent.parent  # dados/dbt
_TARGET = _AQUI / "target"
_MODELS = _AQUI / "models"

# Texto de abertura por camada (o manifest não tem prosa a nível de camada).
_CAMADAS = {
    "bronze": ("Bronze", "Landing bruto, carregado pelo passo EL em Python. Só as colunas necessárias (minimização LGPD)."),
    "silver": ("Silver", "Casos limpos, tipados e deduplicados, com marcadores de negócio. Ainda a nível de caso, não é servido."),
    "gold": ("Gold", "Star schema servido ao backend e ao Grafana. Só agregados cruzam a fronteira (LGPD)."),
}

_AVISO = "<!-- GERADO por scripts/gerar_readmes.py a partir dos artefatos do dbt. Não edite à mão. -->"


def _tipos_do_catalogo() -> dict[str, dict[str, str]]:
    """unique_id → {coluna: tipo} a partir do catalog.json (se existir)."""
    cat = _TARGET / "catalog.json"
    if not cat.exists():
        return {}
    dados = json.loads(cat.read_text())
    saida: dict[str, dict[str, str]] = {}
    for uid, node in {**dados.get("nodes", {}), **dados.get("sources", {})}.items():
        saida[uid] = {c["name"]: (c.get("type") or "") for c in node.get("columns", {}).values()}
    return saida


def _objetos_por_camada(manifest: dict, tipos: dict[str, dict[str, str]]) -> dict[str, list[dict]]:
    camadas: dict[str, list[dict]] = {c: [] for c in _CAMADAS}
    fontes = {uid: (s, "source") for uid, s in manifest.get("sources", {}).items()}
    modelos = {
        uid: (n, "model")
        for uid, n in manifest.get("nodes", {}).items()
        if n.get("resource_type") == "model"
    }
    for uid, (node, tipo) in {**fontes, **modelos}.items():
        partes = node["original_file_path"].split("/")
        if len(partes) < 2 or partes[0] != "models" or partes[1] not in camadas:
            continue
        materializacao = "source (via EL)" if tipo == "source" else node["config"]["materialized"]
        camadas[partes[1]].append({
            "nome": node["name"],
            "schema": node["schema"],
            "materializacao": materializacao,
            "descricao": (node.get("description") or "").strip(),
            "tipo": tipo,
            "colunas": [
                {"nome": c["name"], "tipo": tipos.get(uid, {}).get(c["name"], ""),
                 "descricao": (c.get("description") or "").strip()}
                for c in node.get("columns", {}).values()
            ],
        })
    # fontes primeiro, depois modelos por nome
    for c in camadas:
        camadas[c].sort(key=lambda o: (o["tipo"] != "source", o["nome"]))
    return camadas


def _render(camada: str, objetos: list[dict]) -> str:
    titulo, intro = _CAMADAS[camada]
    linhas = [_AVISO, "", f"# {titulo}", "", intro, ""]
    for o in objetos:
        linhas.append(f"## `{o['schema']}.{o['nome']}` ({o['materializacao']})")
        if o["descricao"]:
            linhas += ["", o["descricao"]]
        if o["colunas"]:
            linhas += ["", "| Coluna | Tipo | Descrição |", "|---|---|---|"]
            for c in o["colunas"]:
                linhas.append(f"| `{c['nome']}` | {c['tipo']} | {c['descricao']} |")
        linhas.append("")
    linhas += [
        "---",
        "Documentação completa, com testes e lineage, no site do dbt. Rode `dbt docs generate && "
        "dbt docs serve` ou `docker compose --profile docs up dbt-docs` (porta 8080).",
        "",
    ]
    return "\n".join(linhas)


def main() -> None:
    manifest_path = _TARGET / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit("manifest.json não encontrado — rode `dbt docs generate` (ou `dbt parse`) antes.")
    manifest = json.loads(manifest_path.read_text())
    tipos = _tipos_do_catalogo()
    por_camada = _objetos_por_camada(manifest, tipos)
    for camada, objetos in por_camada.items():
        destino = _MODELS / camada / "README.md"
        destino.write_text(_render(camada, objetos))
        print(f"escrito {destino.relative_to(_AQUI.parent.parent)} ({len(objetos)} objetos)")


if __name__ == "__main__":
    main()
