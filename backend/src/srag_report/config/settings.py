"""Configuração 12-factor — lê o ambiente (.env). Nenhum segredo no código.

Ver vault/arquitetura/dados-sensiveis.md e adr-0013-containerizacao.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Postgres ──
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "srag"
    postgres_password: str = "srag"
    postgres_db: str = "srag"

    # ── App ──
    log_level: str = "INFO"
    report_dir: str = "data/processed"

    # ── OpenRouter (LLM) ──
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model_orchestration: str = "anthropic/claude-haiku-4.5"
    openrouter_model_narrative: str = "anthropic/claude-haiku-4.5"

    # ── NewsAPI ──
    newsapi_key: str = ""
    # Tracing de LLM: via OpenRouter Broadcast → LangSmith (painel do OpenRouter, sem código).

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
