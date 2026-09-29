from tests.conftest import TEST_TEXT


async def test_search_returns_document(client, document):
    response = await client.get("/search", params={"query": TEST_TEXT})

    assert response.status_code == 200
    body = response.json()
    assert document.id in [item["id"] for item in body]
    assert set(body[0]) == {"id", "rubrics", "text", "created_date"}


async def test_search_empty_query(client):
    response = await client.get("/search", params={"query": ""})

    assert response.status_code == 422


async def test_delete_document(client, document):
    response = await client.delete(f"/documents/{document.id}")
    assert response.status_code == 204

    response = await client.get("/search", params={"query": TEST_TEXT})
    assert document.id not in [item["id"] for item in response.json()]


async def test_delete_missing_document(client):
    response = await client.delete("/documents/999999999")

    assert response.status_code == 404
