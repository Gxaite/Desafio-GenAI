"""Ponto de entrada do ETL.

Placeholder da Fase 1 — a lógica real (extract/clean/dedupe/load) entra na Fase 2.
Ver vault/arquitetura/camada-dados.md.
"""

from __future__ import annotations

import structlog

log = structlog.get_logger()


def main() -> None:
    log.info("etl.start", fase="scaffold")
    # TODO Fase 2:
    #   1. extract  — ler data/raw/srag/*.csv (delimitador ';', encoding latin-1)
    #   2. clean    — datas ISO, normalizar EVOLUCAO/UTI/VACINA_COV, ausentes
    #   3. dedupe   — unir 2025+2026 sem duplicar casos de virada de ano
    #   4. anonimizar — remover identificadores (só agregados cruzam a fronteira)
    #   5. aggregate — marts por dia / mês / recorte
    #   6. load     — gravar marts no Postgres
    log.info("etl.done", msg="scaffold ok — sem carga ainda")


if __name__ == "__main__":
    main()
