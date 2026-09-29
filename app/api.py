from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import DocumentResponse
from app.service import delete_document, search_documents

router = APIRouter()


@router.get(
    "/search",
    response_model=list[DocumentResponse],
    summary="Поиск документов по тексту",
    description="Возвращает до 20 наиболее релевантных документов, отсортированных по дате создания",
)
async def search_doc(
    query: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
):
    return await search_documents(session, query)


@router.delete(
    "/documents/{doc_id}",
    status_code=204,
    summary="Удалить документ",
    description="Удаляет документ из БД и поискового индекса",
    responses={404: {"description": "Документ не найден"}},
)
async def delete_doc(doc_id: int, session: AsyncSession = Depends(get_session)):
    deleted = await delete_document(session, doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Документ не найден")
