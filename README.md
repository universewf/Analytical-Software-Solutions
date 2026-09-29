# Document Search Service

Сервис поиска по текстам документов. Документы хранятся в PostgreSQL,
полнотекстовый индекс — в Elasticsearch. Стек: FastAPI, SQLAlchemy (async), asyncpg,
elasticsearch-py (async).

## Требования

- Docker
- Docker Compose

## Запуск

```bash
# 1. Поднять Postgres, Elasticsearch и сервис.
#    Таблица и индекс создаются автоматически при старте.
docker compose up -d --build

# 2. Загрузить данные из CSV в БД и индекс (выполняется один раз).
docker compose exec app python -m scripts.load_data posts.csv
```

Сервис доступен на `http://localhost:8000`, Swagger UI — `http://localhost:8000/docs`.

## API

### `GET /search?query=<текст>`

Полнотекстовый поиск по полю `text`. Возвращает до 20 наиболее релевантных
документов со всеми полями БД, отсортированных по дате создания (новые первые).

```bash
curl "http://localhost:8000/search?query=конкурс"
```

### `DELETE /documents/{id}`

Удаляет документ из БД и из индекса.

- `204` — удалён
- `404` — документ не найден

```bash
curl -X DELETE http://localhost:8000/documents/1
```

## Документация

`docs.json` — OpenAPI-схема сервиса. Перегенерация после изменения API:

```bash
python -m scripts.export_openapi
```

## Принятые решения

- **Сортировка по дате.** По ТЗ индекс содержит только `id` и `text`, поэтому
  Elasticsearch возвращает 20 наиболее релевантных `id`, а сортировка по
  `created_date` выполняется на стороне БД.
- **Идентификаторы.** `_id` документа в индексе совпадает с `id` в БД — удаление
  из индекса не требует поиска.
- **Рубрики.** В CSV поле `rubrics` хранится как python-литерал списка
  (`['VK-1', 'VK-2']`), разбирается через `ast.literal_eval`.

## Локальный запуск без Docker

```bash
docker compose up -d postgres elasticsearch
cp .env.example .env
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m scripts.load_data posts.csv
uvicorn app.main:app --reload
```

## Структура проекта

```
app/
  main.py      — приложение, lifespan (создание таблицы и индекса)
  api.py       — HTTP-эндпоинты
  service.py   — бизнес-логика: поиск, удаление
  search.py    — клиент Elasticsearch и операции с индексом
  db.py        — engine, сессии, Base
  models.py    — ORM-модель Document
  schemas.py   — Pydantic-схемы ответов
  config.py    — настройки из окружения
scripts/
  load_data.py       — загрузка CSV в БД и индекс
  export_openapi.py  — выгрузка docs.json
```