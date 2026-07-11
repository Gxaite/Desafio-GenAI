"""Ponto de entrada do ETL de SRAG (job `dados`).

Pipeline: EL (Python → bronze) → dbt build (bronze → silver → gold + testes).
Ver vault/camada-dados.md. Só agregados (gold) são servidos ao backend e ao Grafana.
"""

from __future__ import annotations

import subprocess
import sys

import structlog

from srag_etl.config import settings
from srag_etl.extract_load import carregar_bronze, registrar_execucao

log = structlog.get_logger()


def _run_dbt(*args: str) -> None:
    cmd = ["dbt", *args, "--project-dir", settings.dbt_project_dir,
           "--profiles-dir", settings.dbt_project_dir]
    log.info("dbt.run", cmd=" ".join(cmd))
    proc = subprocess.run(cmd, text=True, capture_output=True)
    for linha in (proc.stdout or "").splitlines():
        log.info("dbt", out=linha)
    if proc.returncode != 0:
        for linha in (proc.stderr or "").splitlines():
            log.error("dbt", err=linha)
        raise SystemExit(f"dbt {' '.join(args)} falhou (rc={proc.returncode})")


def main() -> None:
    raw_dir = settings.srag_raw_dir
    log.info("etl.start", raw_dir=raw_dir, destino=settings.postgres_db)

    resultado = carregar_bronze(settings.database_url, raw_dir)
    registrar_execucao(settings.database_url, resultado)
    log.info("el.done", linhas_lidas=resultado.linhas_lidas, arquivos=resultado.arquivos)

    _run_dbt("build")  # roda models (silver, gold) + testes
    log.info("etl.done")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, SystemExit) as exc:
        log.error("etl.fail", erro=str(exc))
        sys.exit(1)
