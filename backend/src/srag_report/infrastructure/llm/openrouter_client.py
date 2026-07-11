"""Adapter do LLM (Claude via OpenRouter) para o port ModeloLLM.

Usa langchain-openai (`ChatOpenAI` apontado para o base_url do OpenRouter — adr-0001).
Timeout e retries no cliente; falhas viram ErroModeloLLM na fronteira.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from srag_report.domain.errors import ErroModeloLLM


class OpenRouterModeloLLM:
    """Implementa `ModeloLLM` sobre o OpenRouter."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "anthropic/claude-sonnet-5",
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self._chat = ChatOpenAI(
            api_key=api_key,  # type: ignore[arg-type]
            base_url=base_url,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
            temperature=0.2,
        )

    def completar(self, system: str, user: str) -> str:
        try:
            resposta = self._chat.invoke(
                [SystemMessage(content=system), HumanMessage(content=user)]
            )
        except Exception as exc:  # fronteira: SDK → erro de domínio
            raise ErroModeloLLM(f"OpenRouter falhou: {exc}") from exc
        return str(resposta.content)
