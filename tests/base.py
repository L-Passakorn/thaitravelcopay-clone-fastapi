import pytest
import httpx
from httpx import AsyncClient
from flasx.main import app
from sqlmodel import SQLModel

from flasx.models import get_session

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


@pytest.fixture
async def engine():
    """Create test database engine."""
    load_dotenv(dotenv_path=".env.test")
    sql_url = os.getenv("SQLDB_URL")
    engine = create_async_engine(
        sql_url,
        connect_args=(
            {"check_same_thread": False} if sql_url.startswith("sqlite") else {}
        ),
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    """Create test database session."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(session):
    """Create test client with dependency override."""

    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000"
    ) as client:
        yield client

    app.dependency_overrides.clear()
