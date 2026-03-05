import pytest
from fastapi.testclient import TestClient
from main import app
from models.db import fake_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():

    fake_db.clear()
    yield


def test_create_book():
    response = client.post("/books/", json={
        "title": "1984",
        "author": "George Orwell",
        "year": 1949,
        "status": "available"
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "1984"


def test_get_all_books():
    # Додаємо дві книги
    client.post("/books/", json={"title": "Book 1", "author": "Author A", "year": 2000})
    client.post("/books/", json={"title": "Book 2", "author": "Author B", "year": 2010, "status": "checked_out"})

    # Отримуємо всі
    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_books_filtered_by_status():
    client.post("/books/", json={"title": "B1", "author": "A1", "year": 2000, "status": "available"})
    client.post("/books/", json={"title": "B2", "author": "A2", "year": 2001, "status": "checked_out"})

    response = client.get("/books/?status=checked_out")
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "B2"


def test_get_books_sorted():
    client.post("/books/", json={"title": "Zebra", "author": "A", "year": 2020})
    client.post("/books/", json={"title": "Apple", "author": "B", "year": 1990})

    # Сортування по року
    response = client.get("/books/?sort_by=year")
    assert response.json()[0]["title"] == "Apple"


def test_get_book_by_id_not_found():
    import uuid
    random_uuid = str(uuid.uuid4())
    response = client.get(f"/books/{random_uuid}")
    assert response.status_code == 404


def test_delete_book_idempotent():
    # Додаємо книгу
    create_res = client.post("/books/", json={"title": "To Delete", "author": "A", "year": 2020})
    book_id = create_res.json()["id"]

    # Видаляємо (перший раз)
    del_res1 = client.delete(f"/books/{book_id}")
    assert del_res1.status_code == 204

    # Видаляємо (другий раз) - має також повернути 204, не падаючи
    del_res2 = client.delete(f"/books/{book_id}")
    assert del_res2.status_code == 204