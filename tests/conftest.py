import pytest
import asyncio
import os
import tempfile
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from flasx.main import app
from flasx import models


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine with temporary file."""
    # Create a temporary database file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_file.close()
    
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{temp_file.name}",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()
    os.unlink(temp_file.name)


@pytest.fixture
async def test_session(test_engine):
    """Create test database session."""
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_session(test_session):
    """Override the get_session dependency."""
    async def _override_get_session():
        yield test_session
    
    app.dependency_overrides[models.get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client(override_get_session):
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_provinces(test_session):
    """Create test provinces."""
    provinces = [
        models.DBProvince(name="Bangkok", tax_reduction_rate=0.50),
        models.DBProvince(name="Chiang Mai", tax_reduction_rate=0.50),
        models.DBProvince(name="Krabi", tax_reduction_rate=0.50),
        models.DBProvince(name="Lamphun", tax_reduction_rate=0.25),
        models.DBProvince(name="Lampang", tax_reduction_rate=0.25),
    ]
    
    for province in provinces:
        test_session.add(province)
    await test_session.commit()
    
    for province in provinces:
        await test_session.refresh(province)
    
    return provinces


@pytest.fixture
async def test_user(test_session):
    """Create test user."""
    user = models.DBUser(
        email="test@example.com",
        citizen_id="1234567890123",
        first_name="Test",
        last_name="User",
        phone_number="0801234567",
        current_address="Bangkok",
        password=""
    )
    
    await user.set_password("password123")
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    return user


@pytest.fixture
async def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = await client.post(
        "/v1/token",
        data={
            "username": test_user.citizen_id,
            "password": "password123"
        }
    )
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}
