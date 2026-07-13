"""Agendador do explorador de notícias: coleta periódica em background.

Roda dentro do processo do Uvicorn (via lifespan da API), sem cron externo: um loop
asyncio dispara `atualizar_historico` a cada `newsapi_intervalo_horas` horas. A coleta é
bloqueante (httpx/psycopg síncronos), então roda em thread separada para não travar o event
loop. Diferente do caminho de requisição (fail-fast), um ciclo que falha é apenas registrado
e não derruba o loop — o próximo ciclo tenta de novo no horário seguinte.

Pressupõe um único worker do Uvicorn (ver Dockerfile); com múltiplos workers cada um teria seu
próprio agendador, multiplicando as chamadas à NewsAPI.
"""

from __future__ import annotations

import asyncio

import structlog

from srag_report.application.noticias import atualizar_historico
from srag_report.composition import montar_dependencias

log = structlog.get_logger()


async def _ciclo() -> None:
    """Uma coleta. Qualquer erro é registrado, não propagado: um job de background nunca
    derruba o loop — o próximo ciclo tenta de novo (mesma filosofia do health check)."""
    try:
        deps = montar_dependencias()
        novas = await asyncio.to_thread(atualizar_historico, deps.fonte, deps.noticias)
        log.info("noticias.coleta.ok", novas=novas)
    except Exception as exc:  # noqa: BLE001 — background reporta, não propaga
        log.warning("noticias.coleta.falhou", erro=f"{type(exc).__name__}: {exc}")


async def loop_coleta(intervalo_horas: int) -> None:
    """Coleta ao subir e depois a cada `intervalo_horas`, indefinidamente."""
    intervalo_s = intervalo_horas * 3600
    while True:
        await _ciclo()
        await asyncio.sleep(intervalo_s)
