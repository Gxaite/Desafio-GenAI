"""Erros de domínio — explícitos e tipados. Ver vault/qualidade-governanca.md.

A fronteira (adapters) traduz exceções de SDK/infra nestes tipos; o domínio nunca vê
`psycopg.Error`, `requests.HTTPError` etc.
"""

from __future__ import annotations


class SragReportError(Exception):
    """Base de todos os erros do domínio."""


class ErroDados(SragReportError):
    """Falha ao ler/agregar dados (repositório, coluna ausente, período vazio)."""


class ErroFonteNoticias(SragReportError):
    """Fonte de notícias indisponível ou fora do limite."""


class ErroModeloLLM(SragReportError):
    """Falha do LLM/OpenRouter."""


class ErroGuardrail(SragReportError):
    """Violação de guardrail (validação, grounding, vazamento)."""


class ErroConfiguracao(SragReportError):
    """Config/segredo ausente ou inválido (fail-fast no boot)."""
