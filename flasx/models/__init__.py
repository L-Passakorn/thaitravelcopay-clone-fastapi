# Models package
# Import order matters to avoid circular imports

import asyncio
import json
import os
from typing import AsyncIterator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

# Import models after setting up the database components
from .user_model import *
from .province_model import *
from .user_province_model import *

connect_args = {"check_same_thread": False}

engine: AsyncEngine = None


async def init_province_data():
    """Initialize province data from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "provinces.json")

    if not os.path.exists(json_path):
        print(f"Province data file not found: {json_path}")
        return

    async for session in get_session():
        # Check if provinces already exist
        from sqlmodel import select

        result = await session.exec(select(DBProvince))
        existing_provinces = result.all()

        if existing_provinces:
            print("Provinces already exist, skipping initialization")
            return

        # Load and insert province data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Insert primary provinces
        for province_data in data["primary_provinces"]:
            province = DBProvince(
                name=province_data["name"],
                tax_reduction_rate=province_data["tax_reduction_rate"],
            )
            session.add(province)

        # Insert secondary provinces
        for province_data in data["secondary_provinces"]:
            province = DBProvince(
                name=province_data["name"],
                tax_reduction_rate=province_data["tax_reduction_rate"],
            )
            session.add(province)

        await session.commit()
        print("Province data initialized successfully")
        break


async def init_db():
    """Initialize the database engine and create tables."""
    global engine

    engine = create_async_engine(
        "sqlite+aiosqlite:///database.db",
        echo=True,
        future=True,
        connect_args=connect_args,
    )

    await create_db_and_tables()
    await init_province_data()


async def create_db_and_tables():
    """Create database tables."""
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Get async database session."""
    if engine is None:
        raise Exception("Database engine is not initialized. Call init_db() first.")

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def close_db():
    """Close database connection."""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None
