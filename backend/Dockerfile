# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Libs de sistema: WeasyPrint (pango/cairo/gdk-pixbuf/ffi + fontes) e o chromium
# headless empacotado pelo kaleido (export estático dos gráficos Plotly).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libcairo2 libffi8 \
        shared-mime-info fonts-dejavu-core \
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
        libgbm1 libasound2 libatspi2.0-0 libxshmfence1 libx11-6 libxcb1 libxi6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app

# 1) Camada de dependências (cacheada por pyproject+lock): só reinstala se as deps mudarem.
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-emit-project --no-dev --no-hashes -o /tmp/requirements.txt \
    && uv pip install --system --no-cache -r /tmp/requirements.txt

# 2) Código do projeto: mudanças aqui NÃO reinstalam as deps (build leve).
COPY src ./src
RUN uv pip install --system --no-cache --no-deps .

RUN useradd -m app && chown -R app /app
USER app

EXPOSE 8000
CMD ["uvicorn", "srag_report.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
