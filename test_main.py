import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import ASGITransport
from main import app, Base
from database import get_db

# Создаем тестовую БД SQLite в памяти
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_session(test_engine):
    AsyncSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client(async_session, monkeypatch):
    # Переопределяем зависимость get_db
    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/regions", json={"name": "Test", "geojson": "{}"})
        assert response.status_code == 201
        yield client

# ---------- ТЕСТЫ -----------------

@pytest.mark.anyio
async def test_create_region(client):
    response = await client.post(
        "/regions",
        json={"name": "Тестовый регион", "geojson": "{}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Тестовый регион"
    assert "id" in data

@pytest.mark.anyio
async def test_get_regions(client):
    # Теперь получаем список регионов
    response = await client.get("/regions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[2]["name"] == "Test"

@pytest.mark.anyio
async def test_add_data_to_region(client):
    # Сначала создаём регион
    resp1 = await client.post("/regions", json={"name": "Test", "geojson": "{}"})
    region_id = resp1.json()["id"]

    # Добавляем данные к региону
    resp2 = await client.post(
        f"/regions/{region_id}/data/",
        json={"title": "Данные1", "value": 42}
    )
    assert resp2.status_code == 201
    data = resp2.json()
    assert data["title"] == "Данные1"
    assert data["value"] == 42
    assert data["region_id"] == region_id