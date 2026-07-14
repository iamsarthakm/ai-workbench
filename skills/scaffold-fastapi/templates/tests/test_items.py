from unittest.mock import AsyncMock, MagicMock

from app.database import get_db
from app.main import app


def test_get_items_returns_empty_list(client):
    db = AsyncMock()
    # AsyncMock auto-vivifies attribute chains as AsyncMock too, so `.scalars()`
    # would return a coroutine unless the awaited result is pinned to a plain
    # MagicMock — `.scalars()`/`.all()` are sync calls on a real SQLAlchemy Result.
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/items")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_post_item_requires_auth(client):
    response = client.post("/items", json={"name": "test item"})
    assert response.status_code == 401  # HTTPBearer: no Authorization header
