import pytest
from elasticsearch import NotFoundError
from httpx import ASGITransport, AsyncClient

from app import search
from app.db import async_session
from app.main import app, init_storage
from app.models import Document
from datetime import datetime

TEST_TEXT = "pytest уникальный тестовый документ"


@pytest.fixture
async def client():
    await init_storage()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def document():
    """Документ в БД и индексе; после теста удаляется, если ещё существует."""
    async with async_session() as session:
        doc = Document(
            rubrics=["VK-test"],
            text=TEST_TEXT,
            created_date=datetime(2024, 1, 1, 12, 0, 0),
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

    await search.index_document(doc.id, doc.text)
    yield doc

    async with async_session() as session:
        db_doc = await session.get(Document, doc.id)
        if db_doc is not None:
            await session.delete(db_doc)
            await session.commit()
    try:
        await search.delete_document(doc.id)
    except NotFoundError:
        pass
