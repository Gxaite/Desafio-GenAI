"""Configuração 12-factor do ETL — lê o ambiente (.env / compose). Sem segredos no código."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Postgres (destino dos marts) ──
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "srag"
    postgres_password: str = "srag"
    postgres_db: str = "srag"

    # ── Fonte (CSVs brutos; montados read-only no container) ──
    srag_raw_dir: str = "/data/raw/srag"
    # Fallback: se não houver CSV local, o ETL baixa destas URLs (Open DATASUS / S3 público).
    srag_csv_urls: str = (
        "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-06-07-2026.csv,"
        "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2026/INFLUD26-06-07-2026.csv"
    )

    # ── dbt (transformação bronze → silver → gold) ──
    dbt_project_dir: str = "/app/dbt"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def csv_urls(self) -> list[str]:
        return [u.strip() for u in self.srag_csv_urls.split(",") if u.strip()]


settings = Settings()
