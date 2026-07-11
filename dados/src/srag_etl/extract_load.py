"""EL — Extract & Load: CSV bruto de SRAG → camada BRONZE no Postgres.

Este passo apenas **carrega** (não transforma). A transformação bronze→silver→gold é do
dbt. Por LGPD (vault/qualidade-governanca.md) carregamos só as ~6 colunas necessárias às
métricas — minimização na ingestão; nenhum dos 194 campos de microdado além destes entra.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from glob import glob
from pathlib import Path

import psycopg

# Colunas lidas do CSV (das 194) e a ordem da tabela bronze.
_COLUNAS_FONTE = ["NU_NOTIFIC", "DT_SIN_PRI", "SG_UF", "EVOLUCAO", "UTI", "VACINA_COV"]
_COLUNAS_BRONZE = [c.lower() for c in _COLUNAS_FONTE] + ["arquivo_origem"]

_DDL = """
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.srag_raw (
    nu_notific     text,
    dt_sin_pri     text,
    sg_uf          text,
    evolucao       text,
    uti            text,
    vacina_cov     text,
    arquivo_origem text NOT NULL
);

CREATE TABLE IF NOT EXISTS bronze.etl_run (
    id            serial PRIMARY KEY,
    executado_em  timestamptz NOT NULL DEFAULT now(),
    linhas_lidas  bigint      NOT NULL,
    arquivos      text        NOT NULL
);
"""


@dataclass(frozen=True)
class ResultadoEL:
    linhas_lidas: int
    arquivos: list[str]


def carregar_bronze(database_url: str, raw_dir: str) -> ResultadoEL:
    """Trunca e recarrega `bronze.srag_raw` a partir de `raw_dir/srag-*.csv` (idempotente)."""
    arquivos = sorted(glob(f"{raw_dir}/srag-*.csv"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum CSV encontrado em {raw_dir}/srag-*.csv")

    cols = ", ".join(_COLUNAS_BRONZE)
    linhas = 0
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(_DDL)
            cur.execute("TRUNCATE bronze.srag_raw")
            with cur.copy(f"COPY bronze.srag_raw ({cols}) FROM STDIN") as copy:
                for arq in arquivos:
                    origem = Path(arq).name
                    idx = _indices_colunas(arq)
                    with open(arq, encoding="utf-8", newline="") as fh:
                        leitor = csv.reader(fh, delimiter=";", quotechar='"')
                        next(leitor, None)  # pula cabeçalho
                        for campos in leitor:
                            copy.write_row([campos[i] for i in idx] + [origem])
                            linhas += 1
        conn.commit()
    return ResultadoEL(linhas_lidas=linhas, arquivos=[Path(a).name for a in arquivos])


def registrar_execucao(database_url: str, resultado: ResultadoEL) -> None:
    """Grava a proveniência da carga (trilha de governança)."""
    with psycopg.connect(database_url) as conn:
        conn.execute(
            "INSERT INTO bronze.etl_run (linhas_lidas, arquivos) VALUES (%s, %s)",
            (resultado.linhas_lidas, ", ".join(resultado.arquivos)),
        )
        conn.commit()


def _indices_colunas(arquivo: str) -> list[int]:
    """Mapeia as colunas de interesse para seus índices no cabeçalho do CSV."""
    with open(arquivo, encoding="utf-8", newline="") as fh:
        cabecalho = next(csv.reader(fh, delimiter=";", quotechar='"'))
    try:
        return [cabecalho.index(c) for c in _COLUNAS_FONTE]
    except ValueError as exc:  # coluna esperada ausente → falha explícita
        raise ValueError(f"coluna ausente no CSV {arquivo}: {exc}") from exc
