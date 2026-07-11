from fastapi.testclient import TestClient

from srag_report.api.main import app

client = TestClient(app)


def test_health_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_db_responds() -> None:
    # Sem Postgres no ambiente de teste, deve degradar graciosamente (não estourar).
    resp = client.get("/health/db")
    assert resp.status_code == 200
    assert resp.json()["status"] in {"ok", "degraded"}
