from unittest.mock import AsyncMock

from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.main import app


def test_health_live_returns_ok(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_ready_returns_ok_when_database_reachable(client):
    db = AsyncMock()

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/health/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok"}}
    db.execute.assert_awaited_once()


def test_health_ready_returns_503_when_database_unreachable(client):
    db = AsyncMock()
    db.execute = AsyncMock(side_effect=SQLAlchemyError("connection refused"))

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/health/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "checks": {"database": "fail"}}
