# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN uv pip install --system --no-cache .

RUN useradd -m app && chown -R app /app
USER app

EXPOSE 8000
CMD ["uvicorn", "srag_report.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
