"""Загрузка документов из CSV в БД и поисковый индекс.

Запуск из корня проекта:
    python -m scripts.load_data posts.csv

Скрипт одноразовый: при повторном запуске документы добавятся ещё раз.
"""

import ast
import asyncio
import csv
import sys
from datetime import datetime

from app.db import async_session
from app.models import Document
from app.search import elastic, index_document


def parse_row(row: dict) -> Document:
    """Преобразовать строку CSV в объект Document.

    rubrics в файле — python-литерал списка ("['VK-1', 'VK-2']"),
    поэтому используется ast.literal_eval, а не json.loads.
    """
    return Document(
        rubrics=ast.literal_eval(row["rubrics"]),
        text=row["text"],
        created_date=datetime.strptime(row["created_date"], "%Y-%m-%d %H:%M:%S"),
    )


async def main(path: str) -> None:
    with open(path, encoding="utf-8", newline="") as f:
        documents = [parse_row(row) for row in csv.DictReader(f)]

    async with async_session() as session:
        session.add_all(documents)
        await session.commit()

    # После commit у объектов заполнен id — он нужен для индекса.
    for doc in documents:
        await index_document(doc.id, doc.text)

    await elastic.close()
    print(f"Загружено документов: {len(documents)}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
