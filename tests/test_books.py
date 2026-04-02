import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from db.session import get_db

MONGO_URL = "mongodb://mongo_admin:password@localhost:27017"

sync_mongo_client = MongoClient(MONGO_URL)


def override_get_db():
    """
    Створюємо клієнт Motor ТУТ.
    """
    client = AsyncIOMotorClient(MONGO_URL)
    try:
        yield client.test_books_db
    finally:
        client.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    sync_mongo_client.drop_database("test_books_db")
    yield
    sync_mongo_client.drop_database("test_books_db")


def test_create_book():
    """Перевіряємо, чи працює створення книги у Mongo"""
    response = client.post(
        "/books/",
        json={
            "title": "Тестова книга Mongo",
            "author": "Тестовий автор",
            "description": "Перевірка тестів",
            "year": 2024,
            "status": "available"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестова книга Mongo"

    assert "_id" in data or "id" in data


def test_get_all_books():
    """Перевіряємо, чи працює отримання списку книг з PaginatedBookResponse"""
    client.post(
        "/books/",
        json={
            "title": "Книга для GET",
            "author": "Автор",
            "description": "Опис",
            "year": 2023,
            "status": "available"
        }
    )

    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()

    assert "books" in data
    assert "count" in data
    assert data["count"] == 1
    assert len(data["books"]) == 1
    assert data["books"][0]["title"] == "Книга для GET"


def test_limit_offset_pagination():
    """Тестуємо логіку Limit-Offset пагінації (Лабораторна 4)"""
    client.post("/books/", json={"title": "Книга 1", "author": "Пагінація Тестер", "year": 2024, "status": "available"})
    client.post("/books/", json={"title": "Книга 2", "author": "Пагінація Тестер", "year": 2024, "status": "available"})

    res_page1 = client.get("/books/?author=Пагінація Тестер&skip=0&limit=1")
    assert res_page1.status_code == 200
    data_page1 = res_page1.json()

    assert data_page1["count"] == 2
    assert len(data_page1["books"]) == 1
    # Безпечно дістаємо id або _id
    book1_id = data_page1["books"][0].get("_id") or data_page1["books"][0].get("id")

    res_page2 = client.get("/books/?author=Пагінація Тестер&skip=1&limit=1")
    assert res_page2.status_code == 200
    data_page2 = res_page2.json()

    assert len(data_page2["books"]) == 1
    book2_id = data_page2["books"][0].get("_id") or data_page2["books"][0].get("id")

    assert book1_id != book2_id