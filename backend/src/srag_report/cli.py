"""CLI para gerar o relatório de SRAG em PDF (entrypoint local / job)."""

from __future__ import annotations

from pathlib import Path

import structlog

from srag_report.application.relatorio import gerar_relatorio_pdf
from srag_report.composition import montar_dependencias
from srag_report.config.settings import settings

log = structlog.get_logger()


def main() -> None:
    repo, fonte, llm = montar_dependencias()
    log.info("relatorio.start", modelo=settings.openrouter_model_narrative)
    pdf, estado = gerar_relatorio_pdf(repo, fonte, llm, settings.openrouter_model_narrative)

    destino = Path(settings.report_dir) / f"relatorio-srag-{estado['referencia']}.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(pdf)

    log.info(
        "relatorio.done",
        arquivo=str(destino),
        bytes=len(pdf),
        run_id=estado["run_id"],
        trilha=[e.no for e in estado["trilha"]],
    )


if __name__ == "__main__":
    main()
