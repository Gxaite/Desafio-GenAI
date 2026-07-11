set dotenv-load := true

# Sobe API + Postgres + Grafana (sem o job de ETL)
up:
    docker compose up -d --build postgres backend grafana

# Roda o ETL (job pontual) → carrega marts no Postgres
etl:
    docker compose --profile etl run --rm dados

# Derruba tudo
down:
    docker compose down

# Logs em tempo real
logs:
    docker compose logs -f

# Testes do backend
test:
    cd backend && uv run pytest

# Lint + tipos do backend
lint:
    cd backend && uv run ruff check . && uv run mypy src
