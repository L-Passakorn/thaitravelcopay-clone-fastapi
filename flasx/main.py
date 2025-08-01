from contextlib import asynccontextmanager
from fastapi import FastAPI
# from flasx.models import engine
# from sqlmodel import SQLModel

from . import models
from . import routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await models.init_db()
    # async with engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Shutdown
    await models.close_db()


app = FastAPI(lifespan=lifespan)
app.include_router(routers.router)


@app.get("/")
def read_root() -> dict:
    return {"Hello": "World"}


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint for production monitoring."""
    return {"status": "healthy", "service": "flasx"}
