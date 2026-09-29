from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import engine, Base
from app import models  # noqa: F401

# для регистрации document В base.metadata
from app.search import create_index, elastic
from app.api import router as api_router


async def init_storage() -> None:
    """Создать таблицу в БД и индекс в Elasticsearch, если их ещё нет."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_index()


@asynccontextmanager
async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_index()
    yield
    await elastic.close()


app = FastAPI(
    lifespan=lifespan,
    title="Document Search Service",
    description="Полнотекстовый поиск по документам",
)


app.include_router(api_router)
