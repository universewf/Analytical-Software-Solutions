from sqlalchemy.ext.asyncio import AsyncSession
from app import search
from app.models import Document
from sqlalchemy import select


async def search_documents(session: AsyncSession, query: str) -> list[Document]:
    ids = await search.search_documents(query)
    if not ids:
        return []
    request = (
        select(Document)
        .where(Document.id.in_(ids))
        .order_by(Document.created_date.desc())
    )
    result = await session.execute(request)
    return list(result.scalars().all())


async def delete_document(session: AsyncSession, doc_id: int) -> bool:
    doc = await session.get(Document, doc_id)
    if doc is None:
        return False
    await session.delete(doc)
    await session.commit()
    await search.delete_document(doc_id)
    return True
