"""Adapter da NewsAPI para o port FonteNoticias.

Resiliência (vault/qualidade-governanca.md): timeout por chamada, retry com backoff só em
erros transitórios (rede, 429, 5xx). Falha permanente vira ErroFonteNoticias na fronteira;
sem chave configurada, degrada para lista vazia.
"""

from __future__ import annotations

import contextlib
from datetime import date
from typing import Any

import httpx
import structlog
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from srag_report.domain.errors import ErroFonteNoticias
from srag_report.domain.models import Noticia

log = structlog.get_logger()

_STATUS_TRANSITORIOS = {429, 500, 502, 503, 504}


def _e_transitorio(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _STATUS_TRANSITORIOS
    return False


class NewsApiFonteNoticias:
    """Implementa `FonteNoticias` sobre a NewsAPI (https://newsapi.org)."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://newsapi.org/v2",
        timeout: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=timeout)

    def buscar(self, consulta: str, *, limite: int = 5) -> list[Noticia]:
        if not self._api_key:
            log.warning("noticias.sem_chave", msg="NEWSAPI_KEY ausente — degradando p/ []")
            return []
        try:
            dados = self._fetch(consulta, limite)
        except httpx.HTTPError as exc:  # fronteira: SDK → erro de domínio
            raise ErroFonteNoticias(f"NewsAPI falhou: {exc}") from exc
        return [self._para_noticia(a) for a in dados.get("articles", [])]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.2, max=2),
        retry=retry_if_exception(_e_transitorio),
        reraise=True,
    )
    def _fetch(self, consulta: str, limite: int) -> dict[str, Any]:
        resp = self._client.get(
            f"{self._base_url}/everything",
            params={
                "q": consulta,
                "language": "pt",
                "sortBy": "publishedAt",
                "pageSize": limite,
            },
            headers={"X-Api-Key": self._api_key},
        )
        resp.raise_for_status()
        dados: dict[str, Any] = resp.json()
        return dados

    @staticmethod
    def _para_noticia(artigo: dict[str, Any]) -> Noticia:
        publicado = None
        with contextlib.suppress(ValueError, TypeError):
            publicado = date.fromisoformat(str(artigo.get("publishedAt", ""))[:10])
        return Noticia(
            titulo=artigo.get("title") or "(sem título)",
            fonte=(artigo.get("source") or {}).get("name") or "desconhecida",
            url=artigo.get("url") or "",
            publicado_em=publicado,
            descricao=artigo.get("description"),
        )
