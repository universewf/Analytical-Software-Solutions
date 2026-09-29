"""Клиент Elasticsearch и операции с поисковым индексом.

Единственное место в проекте, которое знает об Elasticsearch.
Индекс хранит только два поля из ТЗ: id (id документа в БД) и text.
_id документа в индексе совпадает с id из БД, поэтому удаление
не требует поиска.
"""

from elasticsearch import AsyncElasticsearch

from app.config import settings

INDEX_NAME = "documents"

elastic = AsyncElasticsearch(settings.elasticsearch_url)


async def create_index() -> None:
    """Создать индекс с маппингом, если он ещё не существует.

    Вызывается при старте приложения. Повторный вызов безопасен.
    """
    if not await elastic.indices.exists(index=INDEX_NAME):
        await elastic.indices.create(
            index=INDEX_NAME,
            mappings={
                "properties": {
                    "id": {"type": "integer"},
                    "text": {"type": "text"},
                }
            },
        )


async def index_document(doc_id: int, text: str) -> None:
    """Добавить документ в индекс или перезаписать существующий с тем же id."""
    await elastic.index(
        index=INDEX_NAME,
        id=str(doc_id),
        document={"id": doc_id, "text": text},
        refresh=True,
    )


async def search_documents(query: str) -> list[int]:
    """Полнотекстовый поиск по полю text.

    Возвращает до 20 id документов в порядке релевантности.
    Сортировка по дате создания выполняется на стороне БД,
    так как индекс не хранит дату.
    """
    response = await elastic.search(
        index=INDEX_NAME,
        query={"match": {"text": query}},
        size=20,
    )
    return [hit["_source"]["id"] for hit in response["hits"]["hits"]]


async def delete_document(doc_id: int) -> None:
    """Удалить документ из индекса по id.

    Если документа нет, бросает elasticsearch.NotFoundError —
    обработка на стороне сервисного слоя.
    """
    await elastic.delete(index=INDEX_NAME, id=str(doc_id), refresh=True)
